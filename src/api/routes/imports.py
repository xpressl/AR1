"""
Import API Routes - D08
Handles manual import triggers and import status.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import os
import tempfile

from src.db.connection import get_db
from src.models.import_run import ImportRun
from src.data_pipeline.orchestrator.import_orchestrator import ImportOrchestrator
from src.data_pipeline.scheduler.import_scheduler import get_scheduler

router = APIRouter()


# Pydantic Models
class ImportRequest(BaseModel):
    customers_file_path: Optional[str] = None
    invoices_file_path: Optional[str] = None
    payments_file_path: Optional[str] = None


class ImportRunResponse(BaseModel):
    id: int
    status: str
    started_at: datetime
    finished_at: Optional[datetime]
    customers_imported: int
    customers_updated: int
    invoices_imported: int
    invoices_updated: int
    payments_imported: int
    alerts_generated: int
    alerts_resolved: int
    duration_seconds: Optional[int]

    class Config:
        from_attributes = True


# Background task for running imports
async def run_import_task(
    db_url: str,
    customers_path: Optional[str],
    invoices_path: Optional[str],
    payments_path: Optional[str]
):
    """Background task to run import."""
    from src.db.connection import async_session

    async with async_session() as session:
        orchestrator = ImportOrchestrator(session)
        await orchestrator.run_full_import(
            source="csv",
            customers_path=customers_path,
            invoices_path=invoices_path,
            payments_path=payments_path
        )


# Endpoints

@router.post("/trigger")
async def trigger_import(
    request: ImportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger a manual import.

    Provide file paths to CSV files on the server.
    The import will run in the background.
    """
    if not any([request.customers_file_path, request.invoices_file_path, request.payments_file_path]):
        raise HTTPException(
            status_code=400,
            detail="At least one file path must be provided"
        )

    # Validate paths exist
    for path in [request.customers_file_path, request.invoices_file_path, request.payments_file_path]:
        if path and not os.path.exists(path):
            raise HTTPException(
                status_code=400,
                detail=f"File not found: {path}"
            )

    # Run import in background
    orchestrator = ImportOrchestrator(db)
    result = await orchestrator.run_full_import(
        source="csv",
        customers_path=request.customers_file_path,
        invoices_path=request.invoices_file_path,
        payments_path=request.payments_file_path
    )

    return {
        "status": "completed",
        "result": result
    }


@router.post("/upload")
async def upload_and_import(
    customers_file: Optional[UploadFile] = File(None),
    invoices_file: Optional[UploadFile] = File(None),
    payments_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload CSV files and run import.

    Files are saved temporarily and processed.
    """
    if not any([customers_file, invoices_file, payments_file]):
        raise HTTPException(
            status_code=400,
            detail="At least one file must be uploaded"
        )

    temp_files = []
    customers_path = None
    invoices_path = None
    payments_path = None

    try:
        # Save uploaded files to temp directory
        temp_dir = tempfile.mkdtemp()

        if customers_file:
            customers_path = os.path.join(temp_dir, customers_file.filename)
            with open(customers_path, "wb") as f:
                content = await customers_file.read()
                f.write(content)
            temp_files.append(customers_path)

        if invoices_file:
            invoices_path = os.path.join(temp_dir, invoices_file.filename)
            with open(invoices_path, "wb") as f:
                content = await invoices_file.read()
                f.write(content)
            temp_files.append(invoices_path)

        if payments_file:
            payments_path = os.path.join(temp_dir, payments_file.filename)
            with open(payments_path, "wb") as f:
                content = await payments_file.read()
                f.write(content)
            temp_files.append(payments_path)

        # Run import
        orchestrator = ImportOrchestrator(db)
        result = await orchestrator.run_full_import(
            source="csv",
            customers_path=customers_path,
            invoices_path=invoices_path,
            payments_path=payments_path
        )

        return {
            "status": "completed",
            "result": result
        }

    finally:
        # Cleanup temp files
        for path in temp_files:
            try:
                os.remove(path)
            except:
                pass


@router.get("/history", response_model=List[ImportRunResponse])
async def get_import_history(
    limit: int = 20,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get import run history."""
    query = select(ImportRun)

    if status:
        query = query.where(ImportRun.status == status)

    query = query.order_by(desc(ImportRun.started_at)).limit(limit)

    result = await db.execute(query)
    runs = result.scalars().all()

    return [
        ImportRunResponse(
            id=run.id,
            status=run.status,
            started_at=run.started_at,
            finished_at=run.finished_at,
            customers_imported=run.customers_imported or 0,
            customers_updated=run.customers_updated or 0,
            invoices_imported=run.invoices_imported or 0,
            invoices_updated=run.invoices_updated or 0,
            payments_imported=run.payments_imported or 0,
            alerts_generated=run.alerts_generated or 0,
            alerts_resolved=run.alerts_resolved or 0,
            duration_seconds=run.duration_seconds
        )
        for run in runs
    ]


@router.get("/history/{run_id}")
async def get_import_run_detail(
    run_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed import run info."""
    result = await db.execute(
        select(ImportRun).where(ImportRun.id == run_id)
    )
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="Import run not found")

    return {
        "id": run.id,
        "status": run.status,
        "started_at": run.started_at.isoformat(),
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "duration_seconds": run.duration_seconds,
        "customers_imported": run.customers_imported,
        "customers_updated": run.customers_updated,
        "invoices_imported": run.invoices_imported,
        "invoices_updated": run.invoices_updated,
        "payments_imported": run.payments_imported,
        "alerts_generated": run.alerts_generated,
        "alerts_resolved": run.alerts_resolved,
        "error_message": run.error_message
    }


@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get import scheduler status."""
    scheduler = get_scheduler()
    return scheduler.get_status()


@router.post("/scheduler/job/{job_id}/run")
async def run_scheduled_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger a scheduled job."""
    scheduler = get_scheduler()

    if job_id not in scheduler.jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    result = await scheduler.run_job(job_id, manual=True)
    return result


@router.post("/scheduler/job/{job_id}/enable")
async def enable_job(job_id: str):
    """Enable a scheduled job."""
    scheduler = get_scheduler()

    if not scheduler.enable_job(job_id):
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    return {"message": f"Job {job_id} enabled"}


@router.post("/scheduler/job/{job_id}/disable")
async def disable_job(job_id: str):
    """Disable a scheduled job."""
    scheduler = get_scheduler()

    if not scheduler.disable_job(job_id):
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    return {"message": f"Job {job_id} disabled"}
