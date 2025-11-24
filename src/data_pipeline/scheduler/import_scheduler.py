"""
Import Scheduler - D06
Schedules and manages automated data imports from Epicor.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ImportFrequency(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    TWICE_DAILY = "twice_daily"
    WEEKLY = "weekly"
    ON_DEMAND = "on_demand"


class ImportStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class ImportJob:
    """Represents a scheduled import job."""

    def __init__(
        self,
        job_id: str,
        name: str,
        import_type: str,
        frequency: ImportFrequency,
        handler: Callable,
        enabled: bool = True,
        run_at_hour: Optional[int] = None,
        run_at_minute: int = 0,
        days_of_week: Optional[List[int]] = None
    ):
        self.job_id = job_id
        self.name = name
        self.import_type = import_type
        self.frequency = frequency
        self.handler = handler
        self.enabled = enabled
        self.run_at_hour = run_at_hour
        self.run_at_minute = run_at_minute
        self.days_of_week = days_of_week or [0, 1, 2, 3, 4]  # Mon-Fri by default

        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.last_status: Optional[ImportStatus] = None
        self.last_result: Optional[Dict] = None
        self.run_count: int = 0
        self.error_count: int = 0

    def calculate_next_run(self) -> datetime:
        """Calculate the next run time based on frequency."""
        now = datetime.now()

        if self.frequency == ImportFrequency.ON_DEMAND:
            return None

        if self.frequency == ImportFrequency.HOURLY:
            next_run = now.replace(minute=self.run_at_minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(hours=1)
            return next_run

        if self.frequency == ImportFrequency.DAILY:
            next_run = now.replace(
                hour=self.run_at_hour or 6,
                minute=self.run_at_minute,
                second=0,
                microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        if self.frequency == ImportFrequency.TWICE_DAILY:
            morning = now.replace(hour=6, minute=0, second=0, microsecond=0)
            afternoon = now.replace(hour=14, minute=0, second=0, microsecond=0)

            if now < morning:
                return morning
            elif now < afternoon:
                return afternoon
            else:
                return morning + timedelta(days=1)

        if self.frequency == ImportFrequency.WEEKLY:
            next_run = now.replace(
                hour=self.run_at_hour or 6,
                minute=self.run_at_minute,
                second=0,
                microsecond=0
            )
            while next_run.weekday() not in self.days_of_week or next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        return None

    def should_run_now(self) -> bool:
        """Check if this job should run now."""
        if not self.enabled:
            return False
        if self.frequency == ImportFrequency.ON_DEMAND:
            return False
        if self.next_run is None:
            self.next_run = self.calculate_next_run()
        return datetime.now() >= self.next_run


class ImportScheduler:
    """
    Manages scheduling and execution of data import jobs.
    """

    def __init__(self):
        self.jobs: Dict[str, ImportJob] = {}
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.import_history: List[Dict] = []
        self.max_history = 100

    def register_job(self, job: ImportJob) -> None:
        """Register an import job."""
        job.next_run = job.calculate_next_run()
        self.jobs[job.job_id] = job
        logger.info(f"Registered import job: {job.name} ({job.frequency})")

    def unregister_job(self, job_id: str) -> bool:
        """Unregister an import job."""
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False

    def enable_job(self, job_id: str) -> bool:
        """Enable a job."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = True
            self.jobs[job_id].next_run = self.jobs[job_id].calculate_next_run()
            return True
        return False

    def disable_job(self, job_id: str) -> bool:
        """Disable a job."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = False
            return True
        return False

    async def run_job(self, job_id: str, manual: bool = False) -> Dict:
        """
        Run a specific import job.

        Args:
            job_id: The job to run
            manual: Whether this is a manual trigger

        Returns:
            Result dictionary with status and details
        """
        if job_id not in self.jobs:
            return {"status": "error", "message": f"Job not found: {job_id}"}

        job = self.jobs[job_id]
        start_time = datetime.now()

        logger.info(f"Starting import job: {job.name} (manual={manual})")

        try:
            # Run the job handler
            result = await job.handler()

            # Update job stats
            job.last_run = start_time
            job.run_count += 1
            job.last_result = result

            # Determine status
            if result.get("errors") and len(result.get("errors", [])) > 0:
                if result.get("inserted", 0) > 0 or result.get("updated", 0) > 0:
                    job.last_status = ImportStatus.PARTIAL
                else:
                    job.last_status = ImportStatus.FAILED
                    job.error_count += 1
            else:
                job.last_status = ImportStatus.SUCCESS

            # Calculate next run
            job.next_run = job.calculate_next_run()

            # Record history
            history_entry = {
                "job_id": job_id,
                "job_name": job.name,
                "started_at": start_time.isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "status": job.last_status.value,
                "records_processed": result.get("total_records", 0),
                "inserted": result.get("inserted", 0),
                "updated": result.get("updated", 0),
                "errors": len(result.get("errors", [])),
                "manual": manual
            }
            self._add_to_history(history_entry)

            logger.info(
                f"Completed import job: {job.name} - "
                f"Status: {job.last_status.value}, "
                f"Inserted: {result.get('inserted', 0)}, "
                f"Updated: {result.get('updated', 0)}"
            )

            return {
                "status": job.last_status.value,
                "job_id": job_id,
                "job_name": job.name,
                "result": result,
                "duration_seconds": history_entry["duration_seconds"]
            }

        except Exception as e:
            logger.error(f"Import job failed: {job.name} - {str(e)}")

            job.last_run = start_time
            job.last_status = ImportStatus.FAILED
            job.error_count += 1
            job.next_run = job.calculate_next_run()

            history_entry = {
                "job_id": job_id,
                "job_name": job.name,
                "started_at": start_time.isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "status": ImportStatus.FAILED.value,
                "error": str(e),
                "manual": manual
            }
            self._add_to_history(history_entry)

            return {
                "status": "failed",
                "job_id": job_id,
                "error": str(e)
            }

    async def start(self) -> None:
        """Start the scheduler loop."""
        if self.running:
            return

        self.running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("Import scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler loop."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Import scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop - checks for jobs to run."""
        while self.running:
            try:
                for job_id, job in self.jobs.items():
                    if job.should_run_now():
                        await self.run_job(job_id, manual=False)

                # Sleep for 1 minute before checking again
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {str(e)}")
                await asyncio.sleep(60)

    def _add_to_history(self, entry: Dict) -> None:
        """Add entry to history, maintaining max size."""
        self.import_history.insert(0, entry)
        if len(self.import_history) > self.max_history:
            self.import_history = self.import_history[:self.max_history]

    def get_status(self) -> Dict:
        """Get current scheduler status."""
        jobs_status = []
        for job_id, job in self.jobs.items():
            jobs_status.append({
                "job_id": job.job_id,
                "name": job.name,
                "import_type": job.import_type,
                "frequency": job.frequency.value,
                "enabled": job.enabled,
                "last_run": job.last_run.isoformat() if job.last_run else None,
                "next_run": job.next_run.isoformat() if job.next_run else None,
                "last_status": job.last_status.value if job.last_status else None,
                "run_count": job.run_count,
                "error_count": job.error_count
            })

        return {
            "running": self.running,
            "jobs": jobs_status,
            "recent_history": self.import_history[:10]
        }

    def get_history(
        self,
        limit: int = 50,
        job_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get import history with optional filters."""
        history = self.import_history

        if job_id:
            history = [h for h in history if h.get("job_id") == job_id]

        if status:
            history = [h for h in history if h.get("status") == status]

        return history[:limit]


# Default scheduler instance
_scheduler: Optional[ImportScheduler] = None


def get_scheduler() -> ImportScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = ImportScheduler()
    return _scheduler


async def setup_default_jobs(
    customer_handler: Callable,
    invoice_handler: Callable,
    payment_handler: Callable
) -> ImportScheduler:
    """
    Setup default import jobs.

    Args:
        customer_handler: Async function to import customers
        invoice_handler: Async function to import invoices
        payment_handler: Async function to import payments

    Returns:
        Configured ImportScheduler
    """
    scheduler = get_scheduler()

    # Customer import - daily at 6 AM
    scheduler.register_job(ImportJob(
        job_id="import_customers",
        name="Customer Import",
        import_type="customers",
        frequency=ImportFrequency.DAILY,
        handler=customer_handler,
        run_at_hour=6,
        run_at_minute=0
    ))

    # Invoice import - twice daily
    scheduler.register_job(ImportJob(
        job_id="import_invoices",
        name="Invoice Import",
        import_type="invoices",
        frequency=ImportFrequency.TWICE_DAILY,
        handler=invoice_handler
    ))

    # Payment import - twice daily
    scheduler.register_job(ImportJob(
        job_id="import_payments",
        name="Payment Import",
        import_type="payments",
        frequency=ImportFrequency.TWICE_DAILY,
        handler=payment_handler
    ))

    return scheduler
