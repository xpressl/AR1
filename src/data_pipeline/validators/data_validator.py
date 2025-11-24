"""
Data Validator - D05
Validates data before loading into the AR Control Hub database.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal, InvalidOperation
import re


class DataValidator:
    """
    Validates incoming data from Epicor exports.
    Ensures data integrity before database insertion.
    """

    def __init__(self):
        self.errors: List[str] = []

    def validate_customer(self, data: Dict) -> Dict:
        """
        Validate customer data.

        Returns:
            Dict with 'is_valid' bool and 'errors' list
        """
        self.errors = []

        # Required fields
        self._require_field(data, "epicor_customer_id", ["CustID", "epicor_customer_id"])
        self._require_field(data, "name", ["Name", "name"])

        # Validate email if present
        email = data.get("EMailAddress") or data.get("billing_email")
        if email:
            self._validate_email(email)

        # Validate credit limit
        credit_limit = data.get("CreditLimit") or data.get("credit_limit")
        if credit_limit:
            self._validate_decimal(credit_limit, "credit_limit", min_value=0)

        # Validate balance
        balance = data.get("Balance") or data.get("current_balance")
        if balance:
            self._validate_decimal(balance, "current_balance")

        # Validate dates
        for field in ["LastInvoiceDate", "last_invoice_date", "LastPaymentDate", "last_payment_date"]:
            if data.get(field):
                self._validate_date(data[field], field)

        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors
        }

    def validate_invoice(self, data: Dict) -> Dict:
        """
        Validate invoice data.

        Returns:
            Dict with 'is_valid' bool and 'errors' list
        """
        self.errors = []

        # Required fields
        self._require_field(data, "invoice_number", ["InvoiceNum", "epicor_invoice_number"])

        # Require customer reference
        if not (data.get("customer_id") or data.get("CustID") or data.get("epicor_customer_id")):
            self.errors.append("Customer reference is required (customer_id or epicor_customer_id)")

        # Validate amounts
        original = data.get("InvoiceAmt") or data.get("original_amount")
        if original:
            self._validate_decimal(original, "original_amount")

        open_balance = data.get("OpenBalance") or data.get("open_balance")
        if open_balance:
            self._validate_decimal(open_balance, "open_balance")

        # Validate dates
        invoice_date = data.get("InvoiceDate") or data.get("invoice_date")
        if invoice_date:
            self._validate_date(invoice_date, "invoice_date")

        due_date = data.get("DueDate") or data.get("due_date")
        if due_date:
            self._validate_date(due_date, "due_date")

        # Due date should be >= invoice date
        if invoice_date and due_date:
            inv_dt = self._parse_date(invoice_date)
            due_dt = self._parse_date(due_date)
            if inv_dt and due_dt and due_dt < inv_dt:
                self.errors.append("Due date cannot be before invoice date")

        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors
        }

    def validate_payment(self, data: Dict) -> Dict:
        """
        Validate payment data.

        Returns:
            Dict with 'is_valid' bool and 'errors' list
        """
        self.errors = []

        # Required fields
        self._require_field(data, "payment_id", ["PaymentNum", "epicor_payment_id"])

        # Require customer reference
        if not (data.get("customer_id") or data.get("CustID") or data.get("epicor_customer_id")):
            self.errors.append("Customer reference is required")

        # Validate amount
        amount = data.get("PayAmt") or data.get("amount")
        if amount:
            self._validate_decimal(amount, "amount", min_value=0)
        else:
            self.errors.append("Payment amount is required")

        # Validate date
        payment_date = data.get("PayDate") or data.get("payment_date")
        if payment_date:
            self._validate_date(payment_date, "payment_date")

        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors
        }

    def validate_batch(
        self,
        records: List[Dict],
        record_type: str
    ) -> Dict:
        """
        Validate a batch of records.

        Args:
            records: List of record dictionaries
            record_type: 'customer', 'invoice', or 'payment'

        Returns:
            Dict with summary statistics and detailed errors
        """
        validators = {
            "customer": self.validate_customer,
            "invoice": self.validate_invoice,
            "payment": self.validate_payment
        }

        if record_type not in validators:
            return {
                "is_valid": False,
                "total_records": len(records),
                "valid_records": 0,
                "invalid_records": len(records),
                "errors": [{"row": 0, "errors": [f"Unknown record type: {record_type}"]}]
            }

        validator = validators[record_type]
        valid_count = 0
        invalid_count = 0
        all_errors = []

        for idx, record in enumerate(records):
            result = validator(record)
            if result["is_valid"]:
                valid_count += 1
            else:
                invalid_count += 1
                all_errors.append({
                    "row": idx + 1,
                    "errors": result["errors"]
                })

        return {
            "is_valid": invalid_count == 0,
            "total_records": len(records),
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "errors": all_errors
        }

    # Helper methods

    def _require_field(self, data: Dict, field_name: str, possible_keys: List[str]) -> bool:
        """Check that at least one of the possible keys has a value."""
        for key in possible_keys:
            if data.get(key):
                return True
        self.errors.append(f"Required field missing: {field_name}")
        return False

    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email:
            return True
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, str(email)):
            self.errors.append(f"Invalid email format: {email}")
            return False
        return True

    def _validate_decimal(
        self,
        value: Any,
        field_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> bool:
        """Validate decimal/numeric value."""
        try:
            # Clean string values
            if isinstance(value, str):
                value = value.replace("$", "").replace(",", "").strip()

            decimal_val = Decimal(str(value))

            if min_value is not None and decimal_val < Decimal(str(min_value)):
                self.errors.append(f"{field_name} must be >= {min_value}")
                return False

            if max_value is not None and decimal_val > Decimal(str(max_value)):
                self.errors.append(f"{field_name} must be <= {max_value}")
                return False

            return True
        except (InvalidOperation, ValueError, TypeError):
            self.errors.append(f"Invalid numeric value for {field_name}: {value}")
            return False

    def _validate_date(self, value: Any, field_name: str) -> bool:
        """Validate date value."""
        if value is None:
            return True
        if isinstance(value, datetime):
            return True

        parsed = self._parse_date(value)
        if parsed is None:
            self.errors.append(f"Invalid date format for {field_name}: {value}")
            return False
        return True

    def _parse_date(self, value: Any) -> Optional[datetime]:
        """Parse date from various formats."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value

        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue
        return None


class DataQualityChecker:
    """
    Performs data quality checks on imported data.
    Identifies potential issues and anomalies.
    """

    def __init__(self):
        self.warnings: List[Dict] = []

    def check_customer_quality(self, data: Dict) -> List[Dict]:
        """Check customer data quality and return warnings."""
        self.warnings = []

        # Check for missing optional but important fields
        if not (data.get("EMailAddress") or data.get("billing_email")):
            self.warnings.append({
                "field": "billing_email",
                "level": "warning",
                "message": "No email address - cannot send automated reminders"
            })

        if not (data.get("PhoneNum") or data.get("billing_phone")):
            self.warnings.append({
                "field": "billing_phone",
                "level": "info",
                "message": "No phone number on file"
            })

        # Check for suspiciously high credit limit
        credit_limit = data.get("CreditLimit") or data.get("credit_limit")
        if credit_limit:
            try:
                limit = Decimal(str(credit_limit).replace("$", "").replace(",", ""))
                if limit > 1000000:
                    self.warnings.append({
                        "field": "credit_limit",
                        "level": "warning",
                        "message": f"Unusually high credit limit: {limit}"
                    })
            except:
                pass

        # Check for inactive status with balance
        status = data.get("InActive") or data.get("status")
        balance = data.get("Balance") or data.get("current_balance")
        if status in [True, "Inactive", "1", "true", "yes"]:
            try:
                bal = Decimal(str(balance or 0).replace("$", "").replace(",", ""))
                if bal > 0:
                    self.warnings.append({
                        "field": "status",
                        "level": "critical",
                        "message": f"Inactive customer has balance: {bal}"
                    })
            except:
                pass

        return self.warnings

    def check_invoice_quality(self, data: Dict) -> List[Dict]:
        """Check invoice data quality and return warnings."""
        self.warnings = []

        # Check for very old invoices
        invoice_date = data.get("InvoiceDate") or data.get("invoice_date")
        if invoice_date:
            try:
                if isinstance(invoice_date, str):
                    for fmt in ["%Y-%m-%d", "%m/%d/%Y"]:
                        try:
                            invoice_date = datetime.strptime(invoice_date, fmt)
                            break
                        except:
                            continue

                if isinstance(invoice_date, datetime):
                    days_old = (datetime.now() - invoice_date).days
                    if days_old > 365:
                        self.warnings.append({
                            "field": "invoice_date",
                            "level": "warning",
                            "message": f"Invoice is over 1 year old ({days_old} days)"
                        })
            except:
                pass

        # Check for negative amounts
        for field in ["original_amount", "open_balance", "InvoiceAmt", "OpenBalance"]:
            val = data.get(field)
            if val:
                try:
                    amount = Decimal(str(val).replace("$", "").replace(",", ""))
                    if amount < 0 and "credit" not in str(data.get("invoice_type", "")).lower():
                        self.warnings.append({
                            "field": field,
                            "level": "warning",
                            "message": f"Negative amount on non-credit invoice: {amount}"
                        })
                except:
                    pass

        return self.warnings
