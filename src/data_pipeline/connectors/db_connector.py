"""
Database Connector for Epicor Eagle

Provides direct read-only database access to Epicor Eagle SQL Server database.
Uses SQLAlchemy for database connections with proper connection pooling
and retry logic for reliability.

IMPORTANT: This connector is READ-ONLY. No write operations are supported.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
import logging

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log,
)

from .base_connector import DataConnector, DataFetchError, ConnectionConfigError
from ..config.epicor_config import EpicorConfig
from ..config.field_mappings import FieldMappings

logger = logging.getLogger(__name__)


class DatabaseConnector(DataConnector):
    """
    Connector for direct database access to Epicor Eagle.

    This connector provides read-only access to the Epicor database
    using SQLAlchemy with SQL Server via ODBC.

    Features:
    - Connection pooling for efficiency
    - Automatic retry with exponential backoff
    - Read-only operations only (safety measure)
    - Health monitoring

    Attributes:
        config: EpicorConfig instance with database settings
        engine: SQLAlchemy engine instance
    """

    # SQL queries for fetching data from Epicor Eagle
    # These may need adjustment based on actual Epicor schema
    QUERY_CUSTOMERS = """
        SELECT
            CustomerID as customer_id,
            CustomerName as name,
            DBAName as dba_name,
            Address1 as address1,
            Address2 as address2,
            City as city,
            State as state,
            ZipCode as zip,
            Email as email,
            Phone as phone,
            ContactName as contact_name,
            SalespersonID as salesperson_id,
            SalespersonName as salesperson_name,
            TermsCode as terms_code,
            CreditLimit as credit_limit,
            Status as status,
            CustomerType as customer_type,
            BranchID as branch_id,
            Department as department,
            TaxStatus as tax_status,
            TaxExemptNumber as tax_exempt_num,
            LastInvoiceDate as last_invoice_date,
            LastPaymentDate as last_payment_date
        FROM Customer
        WHERE Status IN ('A', 'Active')
    """

    QUERY_INVOICES = """
        SELECT
            InvoiceNumber as invoice_number,
            CustomerID as customer_id,
            InvoiceDate as invoice_date,
            DueDate as due_date,
            OriginalAmount as original_amount,
            OpenBalance as open_balance,
            InvoiceType as invoice_type,
            BranchID as branch_id,
            Department as department,
            SalespersonID as salesperson_id,
            JobReference as job_reference,
            POReference as po_reference,
            OrderNumber as order_number
        FROM OpenAR
        WHERE OpenBalance > 0
    """

    QUERY_PAYMENTS = """
        SELECT
            PaymentID as payment_id,
            CustomerID as customer_id,
            PaymentDate as payment_date,
            Amount as amount,
            PaymentType as payment_type,
            CheckNumber as check_number,
            ReferenceNumber as reference_number,
            AppliedInvoices as applied_invoices,
            UnappliedAmount as unapplied_amount
        FROM Payment
        {where_clause}
        ORDER BY PaymentDate DESC
    """

    QUERY_CREDIT_STATUS = """
        SELECT
            CustomerID as customer_id,
            CreditLimit as credit_limit,
            CreditHold as credit_hold,
            HoldReason as hold_reason,
            HoldDate as hold_date
        FROM CustomerCredit
    """

    def __init__(self, config: Optional[EpicorConfig] = None):
        """
        Initialize the database connector.

        Args:
            config: Optional EpicorConfig instance. If not provided,
                    will load from environment variables.
        """
        super().__init__(connector_name="DatabaseConnector")

        self.config = config or EpicorConfig()
        self._engine: Optional[Engine] = None
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate that required database configuration is present."""
        required_fields = ["db_host", "db_name", "db_user", "db_password"]
        missing = []

        for field in required_fields:
            value = getattr(self.config, field, "")
            if not value:
                missing.append(field)

        if missing:
            logger.warning(
                f"Database configuration incomplete. Missing: {missing}. "
                f"Database connector will not be available until configured."
            )

    def _build_connection_string(self) -> str:
        """
        Build the SQLAlchemy connection string for SQL Server.

        Returns:
            Connection string for SQLAlchemy engine
        """
        # URL encode the password to handle special characters
        password = quote_plus(self.config.db_password)

        connection_string = (
            f"mssql+pyodbc://{self.config.db_user}:{password}"
            f"@{self.config.db_host}:{self.config.db_port}/{self.config.db_name}"
            f"?driver={quote_plus(self.config.db_driver)}"
            f"&TrustServerCertificate=yes"
        )

        return connection_string

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(OperationalError),
        before=before_log(logger, logging.WARNING),
        after=after_log(logger, logging.WARNING),
    )
    def connect(self) -> bool:
        """
        Establish connection to the Epicor database.

        Creates a SQLAlchemy engine with connection pooling.

        Returns:
            bool: True if connection successful

        Raises:
            ConnectionConfigError: If configuration is invalid or connection fails
        """
        if not self.config.db_host or not self.config.db_name:
            raise ConnectionConfigError(
                "Database configuration incomplete. "
                "Please set EPICOR_DB_HOST, EPICOR_DB_NAME, EPICOR_DB_USER, and EPICOR_DB_PASSWORD."
            )

        logger.info(f"Connecting to database: {self.config.db_host}/{self.config.db_name}")

        try:
            connection_string = self._build_connection_string()

            self._engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=self.config.connection_timeout,
                pool_recycle=3600,  # Recycle connections after 1 hour
                pool_pre_ping=True,  # Verify connections before use
            )

            # Test the connection
            with self._engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()

            self._connected = True
            self._clear_errors()
            logger.info("Successfully connected to Epicor database")
            return True

        except OperationalError as e:
            error_msg = f"Failed to connect to database: {str(e)}"
            self._log_error(error_msg)
            raise ConnectionConfigError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error connecting to database: {str(e)}"
            self._log_error(error_msg)
            raise ConnectionConfigError(error_msg) from e

    def disconnect(self) -> None:
        """Close the database connection and dispose of the engine."""
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

        self._connected = False
        logger.info("Database connector disconnected")

    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the database connection.

        Verifies:
        - Engine is created
        - Connection can be established
        - Basic query succeeds

        Returns:
            dict: Health check response
        """
        self._last_health_check = datetime.utcnow()

        health_response = {
            "status": "healthy",
            "connection_type": "database",
            "last_check": self._last_health_check.isoformat() + "Z",
            "details": {
                "host": self.config.db_host,
                "database": self.config.db_name,
                "engine_created": self._engine is not None,
                "connection_test": False,
                "tables_accessible": [],
            },
            "errors": [],
        }

        # Check if configured
        if not self.config.db_host:
            health_response["status"] = "unhealthy"
            health_response["errors"].append("Database not configured")
            return health_response

        # Check if engine exists
        if self._engine is None:
            health_response["status"] = "unhealthy"
            health_response["errors"].append("Database engine not initialized")
            return health_response

        try:
            # Test connection
            with self._engine.connect() as conn:
                # Simple query test
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                health_response["details"]["connection_test"] = True

                # Try to get table list
                inspector = inspect(self._engine)
                tables = inspector.get_table_names()
                health_response["details"]["tables_accessible"] = tables[:10]  # First 10 tables

        except OperationalError as e:
            health_response["status"] = "unhealthy"
            health_response["details"]["connection_test"] = False
            health_response["errors"].append(f"Connection test failed: {str(e)}")

        except Exception as e:
            health_response["status"] = "degraded"
            health_response["errors"].append(f"Health check error: {str(e)}")

        return health_response

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OperationalError),
        before=before_log(logger, logging.WARNING),
        after=after_log(logger, logging.WARNING),
    )
    def _execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a read-only query and return results as list of dicts.

        Args:
            query: SQL query to execute
            params: Optional parameters for the query

        Returns:
            List of dictionaries representing each row

        Raises:
            DataFetchError: If query fails
        """
        if self._engine is None:
            raise DataFetchError("Database engine not initialized. Call connect() first.")

        try:
            with self._engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                columns = result.keys()
                rows = result.fetchall()

                # Convert to list of dicts
                records = [dict(zip(columns, row)) for row in rows]

                logger.debug(f"Query returned {len(records)} rows")
                return records

        except OperationalError as e:
            # Let tenacity handle retry
            raise

        except SQLAlchemyError as e:
            raise DataFetchError(
                f"Database query failed: {str(e)}",
                source="database",
                original_error=e,
            )

    def fetch_customers(self) -> List[Dict[str, Any]]:
        """
        Fetch customer master data from the database.

        Returns:
            List of customer dictionaries
        """
        if not self._connected:
            raise DataFetchError("Connector not connected. Call connect() first.")

        logger.info("Fetching customer data from database...")

        try:
            records = self._execute_query(self.QUERY_CUSTOMERS)
            logger.info(f"Fetched {len(records)} customer records from database")
            return records

        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(
                f"Failed to fetch customers from database: {str(e)}",
                source="database",
                original_error=e,
            )

    def fetch_invoices(self) -> List[Dict[str, Any]]:
        """
        Fetch open invoice/AR data from the database.

        Returns:
            List of invoice dictionaries
        """
        if not self._connected:
            raise DataFetchError("Connector not connected. Call connect() first.")

        logger.info("Fetching invoice data from database...")

        try:
            records = self._execute_query(self.QUERY_INVOICES)
            logger.info(f"Fetched {len(records)} invoice records from database")
            return records

        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(
                f"Failed to fetch invoices from database: {str(e)}",
                source="database",
                original_error=e,
            )

    def fetch_payments(
        self,
        since_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch payment transaction data from the database.

        Args:
            since_date: Optional filter to only return payments after this date

        Returns:
            List of payment dictionaries
        """
        if not self._connected:
            raise DataFetchError("Connector not connected. Call connect() first.")

        logger.info("Fetching payment data from database...")

        try:
            # Build where clause for date filter
            where_clause = ""
            params = {}

            if since_date is not None:
                where_clause = "WHERE PaymentDate >= :since_date"
                params["since_date"] = since_date

            query = self.QUERY_PAYMENTS.format(where_clause=where_clause)
            records = self._execute_query(query, params)
            logger.info(f"Fetched {len(records)} payment records from database")
            return records

        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(
                f"Failed to fetch payments from database: {str(e)}",
                source="database",
                original_error=e,
            )

    def fetch_credit_status(self) -> List[Dict[str, Any]]:
        """
        Fetch credit limit and hold status from the database.

        Returns:
            List of credit status dictionaries
        """
        if not self._connected:
            raise DataFetchError("Connector not connected. Call connect() first.")

        logger.info("Fetching credit status data from database...")

        try:
            records = self._execute_query(self.QUERY_CREDIT_STATUS)
            logger.info(f"Fetched {len(records)} credit status records from database")
            return records

        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(
                f"Failed to fetch credit status from database: {str(e)}",
                source="database",
                original_error=e,
            )

    def execute_custom_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a custom read-only query.

        IMPORTANT: Only SELECT statements are allowed. This method
        will raise an error if the query contains write operations.

        Args:
            query: SQL SELECT query to execute
            params: Optional parameters for the query

        Returns:
            List of dictionaries representing results

        Raises:
            DataFetchError: If query is invalid or fails
        """
        # Safety check: ensure query is read-only
        query_upper = query.strip().upper()
        write_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]

        for keyword in write_keywords:
            if query_upper.startswith(keyword):
                raise DataFetchError(
                    f"Write operations not allowed. Found: {keyword}",
                    source="database",
                )

        if not query_upper.startswith("SELECT"):
            raise DataFetchError(
                "Only SELECT queries are allowed for read-only access",
                source="database",
            )

        return self._execute_query(query, params)

    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Get column names for a specific table.

        Args:
            table_name: Name of the table

        Returns:
            List of column names
        """
        if self._engine is None:
            return []

        try:
            inspector = inspect(self._engine)
            columns = inspector.get_columns(table_name)
            return [col["name"] for col in columns]
        except Exception as e:
            logger.error(f"Failed to get columns for table {table_name}: {e}")
            return []
