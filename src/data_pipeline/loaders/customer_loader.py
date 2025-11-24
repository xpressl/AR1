"""
Customer Loader - D04
Loads and upserts customer data from Epicor into the AR Control Hub database.
"""
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.models.customer import Customer
from src.data_pipeline.validators.data_validator import DataValidator


class CustomerLoader:
    """
    Handles loading customer data from Epicor exports into the database.
    Supports both full loads and incremental updates.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.validator = DataValidator()
        self.stats = {
            "total_records": 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }

    async def load_customers(
        self,
        customers: List[Dict],
        mode: str = "upsert"
    ) -> Dict:
        """
        Load customers into database.

        Args:
            customers: List of customer dictionaries from Epicor
            mode: 'upsert' (insert or update), 'insert_only', 'update_only'

        Returns:
            Statistics dictionary with counts and errors
        """
        self.stats = {
            "total_records": len(customers),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }

        for idx, customer_data in enumerate(customers):
            try:
                # Validate data
                validation_result = self.validator.validate_customer(customer_data)
                if not validation_result["is_valid"]:
                    self.stats["errors"].append({
                        "row": idx + 1,
                        "epicor_id": customer_data.get("epicor_customer_id"),
                        "errors": validation_result["errors"]
                    })
                    self.stats["skipped"] += 1
                    continue

                # Transform data
                transformed = self._transform_customer(customer_data)

                # Upsert to database
                result = await self._upsert_customer(transformed, mode)
                if result == "inserted":
                    self.stats["inserted"] += 1
                elif result == "updated":
                    self.stats["updated"] += 1
                else:
                    self.stats["skipped"] += 1

            except Exception as e:
                self.stats["errors"].append({
                    "row": idx + 1,
                    "epicor_id": customer_data.get("epicor_customer_id"),
                    "errors": [str(e)]
                })
                self.stats["skipped"] += 1

        await self.db.commit()
        return self.stats

    def _transform_customer(self, data: Dict) -> Dict:
        """Transform Epicor customer data to internal format."""
        return {
            "epicor_customer_id": str(data.get("CustID") or data.get("epicor_customer_id", "")).strip(),
            "name": str(data.get("Name") or data.get("name", "")).strip(),
            "dba_trade_name": data.get("DBAName") or data.get("dba_trade_name"),
            "billing_email": data.get("EMailAddress") or data.get("billing_email"),
            "billing_phone": data.get("PhoneNum") or data.get("billing_phone"),
            "primary_contact_name": data.get("PrimContact") or data.get("primary_contact_name"),
            "billing_address_line1": data.get("Address1") or data.get("billing_address_line1"),
            "billing_address_line2": data.get("Address2") or data.get("billing_address_line2"),
            "billing_city": data.get("City") or data.get("billing_city"),
            "billing_state": data.get("State") or data.get("billing_state"),
            "billing_zip": data.get("Zip") or data.get("billing_zip"),
            "salesperson_id": data.get("SalesRepCode") or data.get("salesperson_id"),
            "terms_code": data.get("TermsCode") or data.get("terms_code"),
            "credit_limit": self._parse_decimal(data.get("CreditLimit") or data.get("credit_limit")),
            "status": self._map_status(data.get("InActive") or data.get("status")),
            "customer_type": data.get("CustType") or data.get("customer_type"),
            "branch_id": data.get("BranchID") or data.get("branch_id"),
            "current_balance": self._parse_decimal(data.get("Balance") or data.get("current_balance")),
            "last_invoice_date": self._parse_date(data.get("LastInvoiceDate") or data.get("last_invoice_date")),
            "last_payment_date": self._parse_date(data.get("LastPaymentDate") or data.get("last_payment_date")),
            "updated_at": datetime.utcnow()
        }

    def _parse_decimal(self, value) -> Optional[Decimal]:
        """Parse a value to Decimal, handling various formats."""
        if value is None or value == "":
            return Decimal("0")
        try:
            # Remove currency symbols and commas
            if isinstance(value, str):
                value = value.replace("$", "").replace(",", "").strip()
            return Decimal(str(value))
        except:
            return Decimal("0")

    def _parse_date(self, value) -> Optional[datetime]:
        """Parse various date formats."""
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        try:
            # Try common formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(str(value), fmt)
                except ValueError:
                    continue
            return None
        except:
            return None

    def _map_status(self, value) -> str:
        """Map Epicor status to internal status."""
        if value is None:
            return "Active"
        if isinstance(value, bool):
            return "Inactive" if value else "Active"
        if str(value).lower() in ["true", "1", "yes", "inactive"]:
            return "Inactive"
        if str(value).lower() in ["false", "0", "no", "active"]:
            return "Active"
        return str(value)

    async def _upsert_customer(self, data: Dict, mode: str) -> str:
        """
        Insert or update customer record.
        Returns: 'inserted', 'updated', or 'skipped'
        """
        # Check if customer exists
        result = await self.db.execute(
            select(Customer).where(
                Customer.epicor_customer_id == data["epicor_customer_id"]
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            if mode == "insert_only":
                return "skipped"
            # Update existing
            for key, value in data.items():
                if key != "epicor_customer_id" and value is not None:
                    setattr(existing, key, value)
            return "updated"
        else:
            if mode == "update_only":
                return "skipped"
            # Insert new
            data["created_at"] = datetime.utcnow()
            new_customer = Customer(**data)
            self.db.add(new_customer)
            return "inserted"


class InvoiceLoader:
    """
    Handles loading invoice data from Epicor exports into the database.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.validator = DataValidator()
        self.stats = {
            "total_records": 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }

    async def load_invoices(
        self,
        invoices: List[Dict],
        mode: str = "upsert"
    ) -> Dict:
        """Load invoices into database."""
        from src.models.invoice import Invoice

        self.stats = {
            "total_records": len(invoices),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }

        for idx, invoice_data in enumerate(invoices):
            try:
                # Validate
                validation_result = self.validator.validate_invoice(invoice_data)
                if not validation_result["is_valid"]:
                    self.stats["errors"].append({
                        "row": idx + 1,
                        "invoice_number": invoice_data.get("epicor_invoice_number"),
                        "errors": validation_result["errors"]
                    })
                    self.stats["skipped"] += 1
                    continue

                # Transform
                transformed = self._transform_invoice(invoice_data)

                # Resolve customer_id from epicor_customer_id
                if "epicor_customer_id" in invoice_data:
                    customer_id = await self._resolve_customer_id(
                        invoice_data["epicor_customer_id"]
                    )
                    if not customer_id:
                        self.stats["errors"].append({
                            "row": idx + 1,
                            "invoice_number": invoice_data.get("epicor_invoice_number"),
                            "errors": ["Customer not found"]
                        })
                        self.stats["skipped"] += 1
                        continue
                    transformed["customer_id"] = customer_id

                # Upsert
                result = await self._upsert_invoice(transformed, mode, Invoice)
                if result == "inserted":
                    self.stats["inserted"] += 1
                elif result == "updated":
                    self.stats["updated"] += 1
                else:
                    self.stats["skipped"] += 1

            except Exception as e:
                self.stats["errors"].append({
                    "row": idx + 1,
                    "invoice_number": invoice_data.get("epicor_invoice_number"),
                    "errors": [str(e)]
                })
                self.stats["skipped"] += 1

        await self.db.commit()
        return self.stats

    def _transform_invoice(self, data: Dict) -> Dict:
        """Transform Epicor invoice data to internal format."""
        from decimal import Decimal

        original = self._parse_decimal(data.get("InvoiceAmt") or data.get("original_amount"))
        open_balance = self._parse_decimal(data.get("OpenBalance") or data.get("open_balance"))

        return {
            "epicor_invoice_number": str(data.get("InvoiceNum") or data.get("epicor_invoice_number", "")).strip(),
            "invoice_date": self._parse_date(data.get("InvoiceDate") or data.get("invoice_date")),
            "due_date": self._parse_date(data.get("DueDate") or data.get("due_date")),
            "original_amount": original,
            "open_balance": open_balance if open_balance else original,
            "invoice_type": data.get("InvoiceType") or data.get("invoice_type") or "invoice",
            "terms_code": data.get("TermsCode") or data.get("terms_code"),
            "po_number": data.get("PONum") or data.get("po_number"),
            "status": self._map_invoice_status(open_balance),
            "updated_at": datetime.utcnow()
        }

    def _parse_decimal(self, value) -> Optional[Decimal]:
        if value is None or value == "":
            return Decimal("0")
        try:
            if isinstance(value, str):
                value = value.replace("$", "").replace(",", "").strip()
            return Decimal(str(value))
        except:
            return Decimal("0")

    def _parse_date(self, value) -> Optional[datetime]:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        try:
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(str(value), fmt)
                except ValueError:
                    continue
            return None
        except:
            return None

    def _map_invoice_status(self, open_balance) -> str:
        if open_balance is None or open_balance <= 0:
            return "paid"
        return "open"

    async def _resolve_customer_id(self, epicor_customer_id: str) -> Optional[int]:
        """Look up internal customer ID from Epicor ID."""
        result = await self.db.execute(
            select(Customer.id).where(
                Customer.epicor_customer_id == epicor_customer_id
            )
        )
        row = result.scalar_one_or_none()
        return row

    async def _upsert_invoice(self, data: Dict, mode: str, Invoice) -> str:
        """Insert or update invoice record."""
        result = await self.db.execute(
            select(Invoice).where(
                Invoice.epicor_invoice_number == data["epicor_invoice_number"]
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            if mode == "insert_only":
                return "skipped"
            for key, value in data.items():
                if key != "epicor_invoice_number" and value is not None:
                    setattr(existing, key, value)
            return "updated"
        else:
            if mode == "update_only":
                return "skipped"
            data["created_at"] = datetime.utcnow()
            new_invoice = Invoice(**data)
            self.db.add(new_invoice)
            return "inserted"


class PaymentLoader:
    """
    Handles loading payment data from Epicor exports into the database.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.validator = DataValidator()
        self.stats = {
            "total_records": 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }

    async def load_payments(
        self,
        payments: List[Dict],
        mode: str = "upsert"
    ) -> Dict:
        """Load payments into database."""
        from src.models.payment import Payment

        self.stats = {
            "total_records": len(payments),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }

        for idx, payment_data in enumerate(payments):
            try:
                transformed = self._transform_payment(payment_data)

                # Resolve customer_id
                if "epicor_customer_id" in payment_data:
                    customer_id = await self._resolve_customer_id(
                        payment_data["epicor_customer_id"]
                    )
                    if not customer_id:
                        self.stats["errors"].append({
                            "row": idx + 1,
                            "payment_id": payment_data.get("epicor_payment_id"),
                            "errors": ["Customer not found"]
                        })
                        self.stats["skipped"] += 1
                        continue
                    transformed["customer_id"] = customer_id

                result = await self._upsert_payment(transformed, mode, Payment)
                if result == "inserted":
                    self.stats["inserted"] += 1
                elif result == "updated":
                    self.stats["updated"] += 1
                else:
                    self.stats["skipped"] += 1

            except Exception as e:
                self.stats["errors"].append({
                    "row": idx + 1,
                    "payment_id": payment_data.get("epicor_payment_id"),
                    "errors": [str(e)]
                })
                self.stats["skipped"] += 1

        await self.db.commit()
        return self.stats

    def _transform_payment(self, data: Dict) -> Dict:
        """Transform Epicor payment data to internal format."""
        amount = self._parse_decimal(data.get("PayAmt") or data.get("amount"))

        return {
            "epicor_payment_id": str(data.get("PaymentNum") or data.get("epicor_payment_id", "")).strip(),
            "payment_date": self._parse_date(data.get("PayDate") or data.get("payment_date")),
            "amount": amount,
            "payment_type": data.get("PayMethod") or data.get("payment_type") or "check",
            "check_number": data.get("CheckNum") or data.get("check_number"),
            "reference_number": data.get("RefNum") or data.get("reference_number"),
            "unapplied_amount": self._parse_decimal(data.get("UnappliedAmt") or data.get("unapplied_amount")),
            "updated_at": datetime.utcnow()
        }

    def _parse_decimal(self, value):
        from decimal import Decimal
        if value is None or value == "":
            return Decimal("0")
        try:
            if isinstance(value, str):
                value = value.replace("$", "").replace(",", "").strip()
            return Decimal(str(value))
        except:
            return Decimal("0")

    def _parse_date(self, value):
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        try:
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(str(value), fmt)
                except ValueError:
                    continue
            return None
        except:
            return None

    async def _resolve_customer_id(self, epicor_customer_id: str) -> Optional[int]:
        result = await self.db.execute(
            select(Customer.id).where(
                Customer.epicor_customer_id == epicor_customer_id
            )
        )
        return result.scalar_one_or_none()

    async def _upsert_payment(self, data: Dict, mode: str, Payment) -> str:
        result = await self.db.execute(
            select(Payment).where(
                Payment.epicor_payment_id == data["epicor_payment_id"]
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            if mode == "insert_only":
                return "skipped"
            for key, value in data.items():
                if key != "epicor_payment_id" and value is not None:
                    setattr(existing, key, value)
            return "updated"
        else:
            if mode == "update_only":
                return "skipped"
            data["created_at"] = datetime.utcnow()
            new_payment = Payment(**data)
            self.db.add(new_payment)
            return "inserted"
