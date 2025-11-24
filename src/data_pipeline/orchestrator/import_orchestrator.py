"""
Import Orchestrator - D07
Coordinates the entire data import process from Epicor.
"""
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.connection import async_session
from src.data_pipeline.connectors.csv_connector import CSVConnector
from src.data_pipeline.loaders.customer_loader import CustomerLoader, InvoiceLoader, PaymentLoader
from src.data_pipeline.validators.data_validator import DataValidator
from src.services.alerts.rules_engine import AlertRulesEngine

logger = logging.getLogger(__name__)


class ImportOrchestrator:
    """
    Orchestrates the complete data import process:
    1. Read data from source (CSV or DB)
    2. Validate data
    3. Load into database
    4. Run alert detection
    5. Update customer balances
    6. Log results
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.csv_connector = CSVConnector()
        self.validator = DataValidator()
        self.results: Dict = {}

    async def run_full_import(
        self,
        source: str = "csv",
        customers_path: Optional[str] = None,
        invoices_path: Optional[str] = None,
        payments_path: Optional[str] = None
    ) -> Dict:
        """
        Run a complete import cycle.

        Args:
            source: 'csv' or 'db' for data source type
            customers_path: Path to customers CSV (if source='csv')
            invoices_path: Path to invoices CSV (if source='csv')
            payments_path: Path to payments CSV (if source='csv')

        Returns:
            Complete results dictionary
        """
        start_time = datetime.now()
        self.results = {
            "started_at": start_time.isoformat(),
            "source": source,
            "customers": None,
            "invoices": None,
            "payments": None,
            "alerts": None,
            "balances_updated": 0,
            "errors": [],
            "status": "running"
        }

        try:
            # Step 1: Import Customers
            if customers_path:
                logger.info(f"Importing customers from {customers_path}")
                self.results["customers"] = await self._import_customers(customers_path)

            # Step 2: Import Invoices
            if invoices_path:
                logger.info(f"Importing invoices from {invoices_path}")
                self.results["invoices"] = await self._import_invoices(invoices_path)

            # Step 3: Import Payments
            if payments_path:
                logger.info(f"Importing payments from {payments_path}")
                self.results["payments"] = await self._import_payments(payments_path)

            # Step 4: Update Customer Balances
            logger.info("Updating customer balances")
            self.results["balances_updated"] = await self._update_customer_balances()

            # Step 5: Run Alert Detection
            logger.info("Running alert detection")
            self.results["alerts"] = await self._run_alert_detection()

            # Step 6: Log Import Run
            await self._log_import_run()

            self.results["status"] = "success"

        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            self.results["status"] = "failed"
            self.results["errors"].append(str(e))

        self.results["completed_at"] = datetime.now().isoformat()
        self.results["duration_seconds"] = (
            datetime.now() - start_time
        ).total_seconds()

        return self.results

    async def _import_customers(self, file_path: str) -> Dict:
        """Import customers from CSV file."""
        try:
            # Read CSV
            data = self.csv_connector.read_file(file_path)
            if not data:
                return {"status": "error", "message": "No data in file"}

            # Validate
            validation = self.validator.validate_batch(data, "customer")
            if validation["invalid_records"] > 0:
                logger.warning(
                    f"Customer validation: {validation['invalid_records']} invalid records"
                )

            # Load
            loader = CustomerLoader(self.db)
            result = await loader.load_customers(data)

            return {
                "total_in_file": len(data),
                "validation": validation,
                "loaded": result
            }

        except Exception as e:
            logger.error(f"Customer import failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _import_invoices(self, file_path: str) -> Dict:
        """Import invoices from CSV file."""
        try:
            data = self.csv_connector.read_file(file_path)
            if not data:
                return {"status": "error", "message": "No data in file"}

            validation = self.validator.validate_batch(data, "invoice")
            if validation["invalid_records"] > 0:
                logger.warning(
                    f"Invoice validation: {validation['invalid_records']} invalid records"
                )

            loader = InvoiceLoader(self.db)
            result = await loader.load_invoices(data)

            return {
                "total_in_file": len(data),
                "validation": validation,
                "loaded": result
            }

        except Exception as e:
            logger.error(f"Invoice import failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _import_payments(self, file_path: str) -> Dict:
        """Import payments from CSV file."""
        try:
            data = self.csv_connector.read_file(file_path)
            if not data:
                return {"status": "error", "message": "No data in file"}

            validation = self.validator.validate_batch(data, "payment")
            if validation["invalid_records"] > 0:
                logger.warning(
                    f"Payment validation: {validation['invalid_records']} invalid records"
                )

            loader = PaymentLoader(self.db)
            result = await loader.load_payments(data)

            return {
                "total_in_file": len(data),
                "validation": validation,
                "loaded": result
            }

        except Exception as e:
            logger.error(f"Payment import failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _update_customer_balances(self) -> int:
        """
        Recalculate customer balances based on open invoices.
        Returns count of customers updated.
        """
        from src.models.customer import Customer
        from src.models.invoice import Invoice
        from sqlalchemy import func

        try:
            # Get sum of open balances per customer
            balance_query = select(
                Invoice.customer_id,
                func.sum(Invoice.open_balance).label('total_balance')
            ).where(
                Invoice.open_balance > 0
            ).group_by(Invoice.customer_id)

            result = await self.db.execute(balance_query)
            balances = {row.customer_id: row.total_balance for row in result}

            # Update all customers
            customers_result = await self.db.execute(select(Customer))
            customers = customers_result.scalars().all()

            updated_count = 0
            for customer in customers:
                new_balance = balances.get(customer.id, 0)
                if customer.current_balance != new_balance:
                    customer.current_balance = new_balance
                    updated_count += 1

            await self.db.commit()
            return updated_count

        except Exception as e:
            logger.error(f"Balance update failed: {str(e)}")
            return 0

    async def _run_alert_detection(self) -> Dict:
        """Run alert detection rules."""
        try:
            alert_engine = AlertRulesEngine(self.db)
            return await alert_engine.run_all_rules()
        except Exception as e:
            logger.error(f"Alert detection failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _log_import_run(self) -> None:
        """Log the import run to the database."""
        from src.models.import_run import ImportRun

        try:
            # Extract stats from results
            customers_loaded = self.results.get("customers", {}).get("loaded", {}) if self.results.get("customers") else {}
            invoices_loaded = self.results.get("invoices", {}).get("loaded", {}) if self.results.get("invoices") else {}
            payments_loaded = self.results.get("payments", {}).get("loaded", {}) if self.results.get("payments") else {}
            alerts_result = self.results.get("alerts", {}) or {}

            import_run = ImportRun(
                started_at=datetime.fromisoformat(self.results["started_at"]),
                finished_at=datetime.now(),
                status="Success" if self.results["status"] == "success" else "Failed",
                error_message=str(self.results.get("errors")) if self.results.get("errors") else None,
                customers_imported=customers_loaded.get("inserted", 0),
                customers_updated=customers_loaded.get("updated", 0),
                invoices_imported=invoices_loaded.get("inserted", 0),
                invoices_updated=invoices_loaded.get("updated", 0),
                payments_imported=payments_loaded.get("inserted", 0),
                alerts_generated=alerts_result.get("created", 0) if isinstance(alerts_result, dict) else 0,
                alerts_resolved=alerts_result.get("resolved", 0) if isinstance(alerts_result, dict) else 0
            )

            self.db.add(import_run)
            await self.db.commit()

        except Exception as e:
            logger.error(f"Failed to log import run: {str(e)}")


class ImportRunner:
    """
    Standalone import runner for use with scheduler.
    """

    @staticmethod
    async def run_scheduled_import() -> Dict:
        """Run a scheduled import using configured paths."""
        import_dir = os.getenv("IMPORT_DIRECTORY", "/data/imports")

        async with async_session() as session:
            orchestrator = ImportOrchestrator(session)

            # Check for files
            customers_path = None
            invoices_path = None
            payments_path = None

            import_path = Path(import_dir)
            if import_path.exists():
                # Look for today's files or latest files
                for pattern, var_name in [
                    ("*customer*.csv", "customers_path"),
                    ("*invoice*.csv", "invoices_path"),
                    ("*payment*.csv", "payments_path")
                ]:
                    files = sorted(import_path.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True)
                    if files:
                        if var_name == "customers_path":
                            customers_path = str(files[0])
                        elif var_name == "invoices_path":
                            invoices_path = str(files[0])
                        elif var_name == "payments_path":
                            payments_path = str(files[0])

            return await orchestrator.run_full_import(
                source="csv",
                customers_path=customers_path,
                invoices_path=invoices_path,
                payments_path=payments_path
            )
