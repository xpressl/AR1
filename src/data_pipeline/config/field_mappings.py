"""
Field Mappings for Epicor Data

Defines the mapping between Epicor field names and internal
standardized field names used throughout the AR Control Hub.

This provides a single source of truth for field transformations,
making it easier to adapt to different Epicor configurations or
handle field name variations.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class DataType(Enum):
    """Data types for field validation and conversion."""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"


@dataclass
class FieldDefinition:
    """Definition of a single field with metadata."""
    source_name: str
    target_name: str
    data_type: DataType
    required: bool = False
    default: Any = None
    description: str = ""


class FieldMappings:
    """
    Static field mappings for Epicor data transformation.

    These mappings define how Epicor CSV column names map to
    the standardized internal field names used in AR Control Hub.

    The mappings support:
    - Simple column rename (source -> target)
    - Field validation (required fields)
    - Data type specification for transformation
    """

    # Customer Master field mappings
    # Maps Epicor CSV columns to internal field names
    CUSTOMER_FIELDS: Dict[str, str] = {
        # Source (Epicor CSV) -> Target (Internal)
        "customer_id": "customer_id",
        "name": "name",
        "dba_name": "dba_name",
        "address1": "address_line1",
        "address2": "address_line2",
        "city": "city",
        "state": "state",
        "zip": "postal_code",
        "email": "email",
        "phone": "phone",
        "contact_name": "primary_contact",
        "salesperson_id": "salesperson_id",
        "salesperson_name": "salesperson_name",
        "terms_code": "payment_terms",
        "credit_limit": "credit_limit",
        "status": "status",
        "customer_type": "customer_type",
        "branch_id": "branch_id",
        "department": "department",
        "tax_status": "tax_status",
        "tax_exempt_num": "tax_exempt_number",
        "last_invoice_date": "last_invoice_date",
        "last_payment_date": "last_payment_date",
    }

    # Open AR / Invoice field mappings
    INVOICE_FIELDS: Dict[str, str] = {
        "invoice_number": "invoice_number",
        "customer_id": "customer_id",
        "invoice_date": "invoice_date",
        "due_date": "due_date",
        "original_amount": "original_amount",
        "open_balance": "balance",
        "invoice_type": "invoice_type",
        "branch_id": "branch_id",
        "department": "department",
        "salesperson_id": "salesperson_id",
        "job_reference": "job_reference",
        "po_reference": "po_number",
        "order_number": "order_number",
    }

    # Payment field mappings
    PAYMENT_FIELDS: Dict[str, str] = {
        "payment_id": "payment_id",
        "customer_id": "customer_id",
        "payment_date": "payment_date",
        "amount": "amount",
        "payment_type": "payment_method",
        "check_number": "check_number",
        "reference_number": "reference",
        "applied_invoices": "applied_invoices",
        "unapplied_amount": "unapplied_amount",
    }

    # Credit Status field mappings
    CREDIT_STATUS_FIELDS: Dict[str, str] = {
        "customer_id": "customer_id",
        "credit_limit": "credit_limit",
        "credit_hold": "is_on_hold",
        "hold_reason": "hold_reason",
        "hold_date": "hold_date",
    }

    # Field definitions with types and validation
    CUSTOMER_FIELD_DEFINITIONS: List[FieldDefinition] = [
        FieldDefinition("customer_id", "customer_id", DataType.STRING, required=True),
        FieldDefinition("name", "name", DataType.STRING, required=True),
        FieldDefinition("dba_name", "dba_name", DataType.STRING),
        FieldDefinition("address1", "address_line1", DataType.STRING),
        FieldDefinition("address2", "address_line2", DataType.STRING),
        FieldDefinition("city", "city", DataType.STRING),
        FieldDefinition("state", "state", DataType.STRING),
        FieldDefinition("zip", "postal_code", DataType.STRING),
        FieldDefinition("email", "email", DataType.STRING),
        FieldDefinition("phone", "phone", DataType.STRING),
        FieldDefinition("contact_name", "primary_contact", DataType.STRING),
        FieldDefinition("salesperson_id", "salesperson_id", DataType.STRING),
        FieldDefinition("salesperson_name", "salesperson_name", DataType.STRING),
        FieldDefinition("terms_code", "payment_terms", DataType.STRING),
        FieldDefinition("credit_limit", "credit_limit", DataType.DECIMAL, default=0.0),
        FieldDefinition("status", "status", DataType.STRING, default="active"),
        FieldDefinition("customer_type", "customer_type", DataType.STRING),
        FieldDefinition("branch_id", "branch_id", DataType.STRING),
        FieldDefinition("department", "department", DataType.STRING),
        FieldDefinition("tax_status", "tax_status", DataType.STRING),
        FieldDefinition("tax_exempt_num", "tax_exempt_number", DataType.STRING),
        FieldDefinition("last_invoice_date", "last_invoice_date", DataType.DATE),
        FieldDefinition("last_payment_date", "last_payment_date", DataType.DATE),
    ]

    INVOICE_FIELD_DEFINITIONS: List[FieldDefinition] = [
        FieldDefinition("invoice_number", "invoice_number", DataType.STRING, required=True),
        FieldDefinition("customer_id", "customer_id", DataType.STRING, required=True),
        FieldDefinition("invoice_date", "invoice_date", DataType.DATE, required=True),
        FieldDefinition("due_date", "due_date", DataType.DATE, required=True),
        FieldDefinition("original_amount", "original_amount", DataType.DECIMAL, required=True),
        FieldDefinition("open_balance", "balance", DataType.DECIMAL, required=True),
        FieldDefinition("invoice_type", "invoice_type", DataType.STRING, default="invoice"),
        FieldDefinition("branch_id", "branch_id", DataType.STRING),
        FieldDefinition("department", "department", DataType.STRING),
        FieldDefinition("salesperson_id", "salesperson_id", DataType.STRING),
        FieldDefinition("job_reference", "job_reference", DataType.STRING),
        FieldDefinition("po_reference", "po_number", DataType.STRING),
        FieldDefinition("order_number", "order_number", DataType.STRING),
    ]

    PAYMENT_FIELD_DEFINITIONS: List[FieldDefinition] = [
        FieldDefinition("payment_id", "payment_id", DataType.STRING, required=True),
        FieldDefinition("customer_id", "customer_id", DataType.STRING, required=True),
        FieldDefinition("payment_date", "payment_date", DataType.DATE, required=True),
        FieldDefinition("amount", "amount", DataType.DECIMAL, required=True),
        FieldDefinition("payment_type", "payment_method", DataType.STRING),
        FieldDefinition("check_number", "check_number", DataType.STRING),
        FieldDefinition("reference_number", "reference", DataType.STRING),
        FieldDefinition("applied_invoices", "applied_invoices", DataType.STRING),
        FieldDefinition("unapplied_amount", "unapplied_amount", DataType.DECIMAL, default=0.0),
    ]

    CREDIT_STATUS_FIELD_DEFINITIONS: List[FieldDefinition] = [
        FieldDefinition("customer_id", "customer_id", DataType.STRING, required=True),
        FieldDefinition("credit_limit", "credit_limit", DataType.DECIMAL, default=0.0),
        FieldDefinition("credit_hold", "is_on_hold", DataType.BOOLEAN, default=False),
        FieldDefinition("hold_reason", "hold_reason", DataType.STRING),
        FieldDefinition("hold_date", "hold_date", DataType.DATE),
    ]

    @classmethod
    def get_required_fields(cls, entity_type: str) -> List[str]:
        """
        Get list of required source field names for an entity type.

        Args:
            entity_type: One of 'customer', 'invoice', 'payment', 'credit_status'

        Returns:
            List of required field names (source names)
        """
        definitions_map = {
            "customer": cls.CUSTOMER_FIELD_DEFINITIONS,
            "invoice": cls.INVOICE_FIELD_DEFINITIONS,
            "payment": cls.PAYMENT_FIELD_DEFINITIONS,
            "credit_status": cls.CREDIT_STATUS_FIELD_DEFINITIONS,
        }

        definitions = definitions_map.get(entity_type, [])
        return [fd.source_name for fd in definitions if fd.required]

    @classmethod
    def get_field_mapping(cls, entity_type: str) -> Dict[str, str]:
        """
        Get field mapping dictionary for an entity type.

        Args:
            entity_type: One of 'customer', 'invoice', 'payment', 'credit_status'

        Returns:
            Dictionary mapping source names to target names
        """
        mapping_map = {
            "customer": cls.CUSTOMER_FIELDS,
            "invoice": cls.INVOICE_FIELDS,
            "payment": cls.PAYMENT_FIELDS,
            "credit_status": cls.CREDIT_STATUS_FIELDS,
        }

        return mapping_map.get(entity_type, {})

    @classmethod
    def get_field_type(cls, entity_type: str, field_name: str) -> Optional[DataType]:
        """
        Get the data type for a specific field.

        Args:
            entity_type: One of 'customer', 'invoice', 'payment', 'credit_status'
            field_name: Source field name

        Returns:
            DataType enum value or None if field not found
        """
        definitions_map = {
            "customer": cls.CUSTOMER_FIELD_DEFINITIONS,
            "invoice": cls.INVOICE_FIELD_DEFINITIONS,
            "payment": cls.PAYMENT_FIELD_DEFINITIONS,
            "credit_status": cls.CREDIT_STATUS_FIELD_DEFINITIONS,
        }

        definitions = definitions_map.get(entity_type, [])
        for fd in definitions:
            if fd.source_name == field_name:
                return fd.data_type

        return None

    @classmethod
    def validate_record(
        cls,
        entity_type: str,
        record: Dict[str, Any],
    ) -> tuple[bool, List[str]]:
        """
        Validate a record against field definitions.

        Args:
            entity_type: One of 'customer', 'invoice', 'payment', 'credit_status'
            record: Dictionary representing a single record

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        required_fields = cls.get_required_fields(entity_type)

        for field in required_fields:
            if field not in record or record[field] is None or record[field] == "":
                errors.append(f"Missing required field: {field}")

        return (len(errors) == 0, errors)


# Alternative field name mappings for different Epicor versions/configs
# These can be used if the source system has different column names
ALTERNATE_CUSTOMER_FIELDS: Dict[str, List[str]] = {
    "customer_id": ["CustomerID", "CUSTID", "CUST_ID", "Customer_ID", "CustomerNo"],
    "name": ["CustomerName", "CUSTNAME", "NAME", "Customer_Name", "CompanyName"],
    "email": ["Email", "EMAIL", "E_Mail", "EmailAddress", "Contact_Email"],
    "phone": ["Phone", "PHONE", "PhoneNumber", "Phone_Number", "MainPhone"],
    "credit_limit": ["CreditLimit", "CREDLIM", "CREDIT_LIMIT", "Credit_Limit"],
}

ALTERNATE_INVOICE_FIELDS: Dict[str, List[str]] = {
    "invoice_number": ["InvoiceNumber", "INVNO", "INV_NO", "Invoice_No", "InvoiceNum"],
    "customer_id": ["CustomerID", "CUSTID", "CUST_ID", "Customer_ID"],
    "invoice_date": ["InvoiceDate", "INVDATE", "INV_DATE", "Invoice_Date"],
    "due_date": ["DueDate", "DUEDATE", "DUE_DATE", "Due_Date"],
    "open_balance": ["OpenBalance", "Balance", "BALANCE", "Open_Balance", "AmountDue"],
}


def find_matching_column(
    target_field: str,
    available_columns: List[str],
    alternate_mappings: Dict[str, List[str]],
) -> Optional[str]:
    """
    Find a matching column name from available columns.

    Useful when dealing with CSV files that may have different
    column naming conventions.

    Args:
        target_field: The internal field name to find
        available_columns: List of column names in the data source
        alternate_mappings: Dictionary of alternative names for each field

    Returns:
        The matching column name or None if not found
    """
    # First, try exact match (case-insensitive)
    target_lower = target_field.lower()
    for col in available_columns:
        if col.lower() == target_lower:
            return col

    # Try alternate names
    alternates = alternate_mappings.get(target_field, [])
    for alt_name in alternates:
        for col in available_columns:
            if col.lower() == alt_name.lower():
                return col

    return None
