"""
CSV Connector for Epicor Eagle Exports

Reads and parses CSV files exported from Epicor Eagle ERP system.
Supports the four main export files:
- CustomerMaster.csv
- OpenAR.csv
- Payments.csv
- CreditStatus.csv
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

import pandas as pd
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


class CSVConnector(DataConnector):
    """
    Connector for reading Epicor CSV export files.

    This connector reads CSV files from a configured directory,
    parses them using pandas, and returns standardized data dictionaries.

    Attributes:
        config: EpicorConfig instance with CSV settings
        import_path: Path to the CSV import directory
        encoding: CSV file encoding
        delimiter: CSV field delimiter
    """

    # Expected CSV file names
    FILE_CUSTOMERS = "CustomerMaster.csv"
    FILE_INVOICES = "OpenAR.csv"
    FILE_PAYMENTS = "Payments.csv"
    FILE_CREDIT = "CreditStatus.csv"

    def __init__(self, config: Optional[EpicorConfig] = None):
        """
        Initialize the CSV connector.

        Args:
            config: Optional EpicorConfig instance. If not provided,
                    will load from environment variables.
        """
        super().__init__(connector_name="CSVConnector")

        self.config = config or EpicorConfig()
        self.import_path = Path(self.config.csv_import_path)
        self.encoding = self.config.csv_encoding
        self.delimiter = self.config.csv_delimiter
        self._file_metadata: Dict[str, Dict[str, Any]] = {}

    def connect(self) -> bool:
        """
        Verify the CSV import directory is accessible.

        Returns:
            bool: True if directory exists and is readable

        Raises:
            ConnectionConfigError: If path doesn't exist or isn't readable
        """
        logger.info(f"Connecting to CSV source at: {self.import_path}")

        try:
            if not self.import_path.exists():
                raise ConnectionConfigError(
                    f"CSV import path does not exist: {self.import_path}"
                )

            if not self.import_path.is_dir():
                raise ConnectionConfigError(
                    f"CSV import path is not a directory: {self.import_path}"
                )

            # Try to list directory to verify read access
            list(self.import_path.iterdir())

            self._connected = True
            self._clear_errors()
            logger.info(f"Successfully connected to CSV source: {self.import_path}")
            return True

        except PermissionError as e:
            error_msg = f"Permission denied accessing: {self.import_path}"
            self._log_error(error_msg)
            raise ConnectionConfigError(error_msg) from e

        except Exception as e:
            error_msg = f"Failed to connect to CSV source: {str(e)}"
            self._log_error(error_msg)
            raise ConnectionConfigError(error_msg) from e

    def disconnect(self) -> None:
        """Close the CSV connection (releases any cached data)."""
        self._connected = False
        self._file_metadata = {}
        logger.info("CSV connector disconnected")

    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the CSV data source.

        Verifies:
        - Import directory is accessible
        - Expected CSV files exist
        - Files are not too old (configurable threshold)

        Returns:
            dict: Health check response
        """
        self._last_health_check = datetime.utcnow()

        health_response = {
            "status": "healthy",
            "connection_type": "csv",
            "last_check": self._last_health_check.isoformat() + "Z",
            "details": {
                "csv_path": str(self.import_path),
                "csv_path_accessible": False,
                "files_found": [],
                "files_missing": [],
                "last_modified": None,
            },
            "errors": [],
        }

        try:
            # Check directory accessibility
            if not self.import_path.exists():
                health_response["status"] = "unhealthy"
                health_response["errors"].append(
                    f"Import path does not exist: {self.import_path}"
                )
                return health_response

            health_response["details"]["csv_path_accessible"] = True

            # Check for expected files
            expected_files = [
                self.FILE_CUSTOMERS,
                self.FILE_INVOICES,
                self.FILE_PAYMENTS,
                self.FILE_CREDIT,
            ]

            latest_modified = None

            for filename in expected_files:
                file_path = self.import_path / filename
                if file_path.exists():
                    health_response["details"]["files_found"].append(filename)
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if latest_modified is None or file_mtime > latest_modified:
                        latest_modified = file_mtime
                else:
                    health_response["details"]["files_missing"].append(filename)

            if latest_modified:
                health_response["details"]["last_modified"] = latest_modified.isoformat() + "Z"

            # Determine overall status
            if health_response["details"]["files_missing"]:
                if len(health_response["details"]["files_found"]) > 0:
                    health_response["status"] = "degraded"
                    health_response["errors"].append(
                        f"Missing files: {', '.join(health_response['details']['files_missing'])}"
                    )
                else:
                    health_response["status"] = "unhealthy"
                    health_response["errors"].append("No CSV files found in import directory")

            # Check file age (warn if older than 24 hours)
            if latest_modified:
                age_hours = (datetime.now() - latest_modified).total_seconds() / 3600
                health_response["details"]["file_age_hours"] = round(age_hours, 1)
                if age_hours > 24:
                    if health_response["status"] == "healthy":
                        health_response["status"] = "degraded"
                    health_response["errors"].append(
                        f"Files are {round(age_hours, 1)} hours old (>24 hours)"
                    )

        except Exception as e:
            health_response["status"] = "unhealthy"
            health_response["errors"].append(f"Health check error: {str(e)}")
            self._log_error(f"Health check failed: {str(e)}")

        return health_response

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((IOError, OSError)),
        before=before_log(logger, logging.WARNING),
        after=after_log(logger, logging.WARNING),
    )
    def _read_csv_file(
        self,
        filename: str,
        required_columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Read and parse a CSV file with retry logic.

        Args:
            filename: Name of the CSV file to read
            required_columns: Optional list of columns that must be present

        Returns:
            pandas DataFrame with the parsed data

        Raises:
            DataFetchError: If file cannot be read or is invalid
        """
        file_path = self.import_path / filename

        if not file_path.exists():
            raise DataFetchError(
                f"CSV file not found: {filename}",
                source=str(file_path),
            )

        # Wait for file to be completely written (check for file lock)
        self._wait_for_file_ready(file_path)

        try:
            # Read CSV file
            df = pd.read_csv(
                file_path,
                encoding=self.encoding,
                delimiter=self.delimiter,
                dtype=str,  # Read all as strings initially
                na_values=["", "NULL", "null", "None", "N/A", "n/a"],
                keep_default_na=True,
            )

            # Strip whitespace from column names
            df.columns = df.columns.str.strip()

            # Store file metadata
            self._file_metadata[filename] = {
                "path": str(file_path),
                "rows": len(df),
                "columns": list(df.columns),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "size_bytes": file_path.stat().st_size,
            }

            # Validate required columns if specified
            if required_columns:
                missing_cols = set(required_columns) - set(df.columns)
                if missing_cols:
                    raise DataFetchError(
                        f"Missing required columns in {filename}: {missing_cols}",
                        source=str(file_path),
                    )

            logger.info(
                f"Read {len(df)} rows from {filename} "
                f"({file_path.stat().st_size / 1024:.1f} KB)"
            )

            return df

        except pd.errors.ParserError as e:
            raise DataFetchError(
                f"Failed to parse CSV file: {filename}",
                source=str(file_path),
                original_error=e,
            )
        except UnicodeDecodeError as e:
            raise DataFetchError(
                f"Encoding error reading {filename}. Expected {self.encoding}",
                source=str(file_path),
                original_error=e,
            )

    def _wait_for_file_ready(
        self,
        file_path: Path,
        max_wait: int = 30,
        check_interval: float = 0.5,
    ) -> None:
        """
        Wait for a file to be completely written (not locked).

        Checks if file size is stable over the check interval.

        Args:
            file_path: Path to the file
            max_wait: Maximum seconds to wait
            check_interval: Seconds between size checks
        """
        start_time = time.time()
        last_size = -1

        while time.time() - start_time < max_wait:
            try:
                current_size = file_path.stat().st_size
                if current_size == last_size and current_size > 0:
                    # Size is stable, file is likely ready
                    return
                last_size = current_size
                time.sleep(check_interval)
            except OSError:
                # File might be locked, wait and retry
                time.sleep(check_interval)

        logger.warning(f"File ready wait timeout for: {file_path}")

    def _dataframe_to_records(
        self,
        df: pd.DataFrame,
        field_mapping: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Convert DataFrame to list of dictionaries with optional field mapping.

        Args:
            df: pandas DataFrame to convert
            field_mapping: Optional dict mapping source columns to target names

        Returns:
            List of dictionaries representing each row
        """
        if field_mapping:
            # Rename columns based on mapping
            rename_dict = {k: v for k, v in field_mapping.items() if k in df.columns}
            df = df.rename(columns=rename_dict)

        # Convert to records, handling NaN values
        records = df.where(pd.notnull(df), None).to_dict(orient="records")

        return records

    def fetch_customers(self) -> List[Dict[str, Any]]:
        """
        Fetch customer master data from CustomerMaster.csv.

        Returns:
            List of customer dictionaries with standardized field names
        """
        if not self._connected:
            raise DataFetchError("Connector not connected. Call connect() first.")

        logger.info("Fetching customer data from CSV...")

        try:
            df = self._read_csv_file(
                self.FILE_CUSTOMERS,
                required_columns=["customer_id", "name"],
            )

            # Apply field mapping
            records = self._dataframe_to_records(
                df,
                field_mapping=FieldMappings.CUSTOMER_FIELDS,
            )

            logger.info(f"Fetched {len(records)} customer records")
            return records

        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(
                f"Failed to fetch customers: {str(e)}",
                source=self.FILE_CUSTOMERS,
                original_error=e,
            )

    def fetch_invoices(self) -> List[Dict[str, Any]]:
        """
        Fetch open invoice/AR data from OpenAR.csv.

        Returns:
            List of invoice dictionaries with standardized field names
        """
        if not self._connected:
            raise DataFetchError("Connector not connected. Call connect() first.")

        logger.info("Fetching invoice data from CSV...")

        try:
            df = self._read_csv_file(
                self.FILE_INVOICES,
                required_columns=["invoice_number", "customer_id"],
            )

            # Convert numeric fields
            numeric_fields = ["original_amount", "open_balance"]
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors="coerce")

            # Convert date fields
            date_fields = ["invoice_date", "due_date"]
            for field in date_fields:
                if field in df.columns:
                    df[field] = pd.to_datetime(df[field], errors="coerce")

            # Apply field mapping
            records = self._dataframe_to_records(
                df,
                field_mapping=FieldMappings.INVOICE_FIELDS,
            )

            logger.info(f"Fetched {len(records)} invoice records")
            return records

        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(
                f"Failed to fetch invoices: {str(e)}",
                source=self.FILE_INVOICES,
                original_error=e,
            )

    def fetch_payments(
        self,
        since_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch payment transaction data from Payments.csv.

        Args:
            since_date: Optional filter to only return payments after this date

        Returns:
            List of payment dictionaries with standardized field names
        """
        if not self._connected:
            raise DataFetchError("Connector not connected. Call connect() first.")

        logger.info("Fetching payment data from CSV...")

        try:
            df = self._read_csv_file(
                self.FILE_PAYMENTS,
                required_columns=["payment_id", "customer_id"],
            )

            # Convert numeric fields
            numeric_fields = ["amount", "unapplied_amount"]
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors="coerce")

            # Convert date fields
            if "payment_date" in df.columns:
                df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")

                # Filter by date if specified
                if since_date is not None:
                    df = df[df["payment_date"] >= pd.Timestamp(since_date)]

            # Apply field mapping
            records = self._dataframe_to_records(
                df,
                field_mapping=FieldMappings.PAYMENT_FIELDS,
            )

            logger.info(f"Fetched {len(records)} payment records")
            return records

        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(
                f"Failed to fetch payments: {str(e)}",
                source=self.FILE_PAYMENTS,
                original_error=e,
            )

    def fetch_credit_status(self) -> List[Dict[str, Any]]:
        """
        Fetch credit limit and hold status from CreditStatus.csv.

        Returns:
            List of credit status dictionaries with standardized field names
        """
        if not self._connected:
            raise DataFetchError("Connector not connected. Call connect() first.")

        logger.info("Fetching credit status data from CSV...")

        try:
            df = self._read_csv_file(
                self.FILE_CREDIT,
                required_columns=["customer_id"],
            )

            # Convert numeric fields
            if "credit_limit" in df.columns:
                df["credit_limit"] = pd.to_numeric(df["credit_limit"], errors="coerce")

            # Convert boolean fields
            if "credit_hold" in df.columns:
                df["credit_hold"] = df["credit_hold"].str.lower().isin(
                    ["true", "yes", "1", "y"]
                )

            # Convert date fields
            if "hold_date" in df.columns:
                df["hold_date"] = pd.to_datetime(df["hold_date"], errors="coerce")

            # Apply field mapping
            records = self._dataframe_to_records(
                df,
                field_mapping=FieldMappings.CREDIT_STATUS_FIELDS,
            )

            logger.info(f"Fetched {len(records)} credit status records")
            return records

        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(
                f"Failed to fetch credit status: {str(e)}",
                source=self.FILE_CREDIT,
                original_error=e,
            )

    def get_file_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata about the CSV files that have been read.

        Returns:
            Dictionary mapping filename to metadata dict
        """
        return self._file_metadata.copy()

    def get_available_files(self) -> List[str]:
        """
        List all CSV files available in the import directory.

        Returns:
            List of CSV filenames found
        """
        if not self._connected:
            return []

        csv_files = []
        for file_path in self.import_path.glob("*.csv"):
            csv_files.append(file_path.name)

        return sorted(csv_files)
