"""
Epicor Configuration Settings

Centralized configuration management for Epicor data connections.
Uses Pydantic BaseSettings for validation and environment variable loading.

Configuration can be set via:
1. Environment variables (prefixed with EPICOR_)
2. .env file in the project root
3. Direct instantiation with keyword arguments

Environment Variables:
    EPICOR_CSV_IMPORT_PATH: Path to CSV import directory
    EPICOR_CSV_ENCODING: CSV file encoding (default: utf-8)
    EPICOR_CSV_DELIMITER: CSV field delimiter (default: ,)
    EPICOR_DB_HOST: Database server hostname
    EPICOR_DB_PORT: Database server port (default: 1433)
    EPICOR_DB_NAME: Database name
    EPICOR_DB_USER: Database username
    EPICOR_DB_PASSWORD: Database password
    EPICOR_DB_DRIVER: ODBC driver name
    EPICOR_CONNECTION_TIMEOUT: Connection timeout in seconds
    EPICOR_MAX_RETRIES: Maximum retry attempts
    EPICOR_RETRY_DELAY: Base delay between retries in seconds
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EpicorConfig(BaseSettings):
    """
    Configuration settings for Epicor data connections.

    This class uses Pydantic's BaseSettings to automatically load
    configuration from environment variables with the EPICOR_ prefix.

    Attributes:
        csv_import_path: Path to the directory containing CSV exports
        csv_encoding: Character encoding for CSV files
        csv_delimiter: Field delimiter for CSV files
        db_host: Database server hostname or IP address
        db_port: Database server port (default 1433 for SQL Server)
        db_name: Name of the Epicor database
        db_user: Database username for authentication
        db_password: Database password for authentication
        db_driver: ODBC driver name for SQL Server connection
        connection_timeout: Timeout for connection attempts in seconds
        max_retries: Maximum number of retry attempts for failed operations
        retry_delay: Base delay between retries (exponential backoff)
    """

    model_config = SettingsConfigDict(
        env_prefix="EPICOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # CSV Import Settings
    csv_import_path: str = Field(
        default="/data/epicor/exports",
        description="Path to the directory containing CSV exports from Epicor",
    )
    csv_encoding: str = Field(
        default="utf-8",
        description="Character encoding for CSV files",
    )
    csv_delimiter: str = Field(
        default=",",
        description="Field delimiter for CSV files",
    )
    csv_date_format: str = Field(
        default="%Y-%m-%d",
        description="Date format string for parsing dates in CSV files",
    )
    csv_datetime_format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="DateTime format string for parsing timestamps in CSV files",
    )

    # Database Connection Settings
    db_host: str = Field(
        default="",
        description="Database server hostname or IP address",
    )
    db_port: int = Field(
        default=1433,
        description="Database server port (default: 1433 for SQL Server)",
    )
    db_name: str = Field(
        default="",
        description="Name of the Epicor database",
    )
    db_user: str = Field(
        default="",
        description="Database username for authentication",
    )
    db_password: str = Field(
        default="",
        description="Database password for authentication",
    )
    db_driver: str = Field(
        default="ODBC Driver 17 for SQL Server",
        description="ODBC driver name for SQL Server connection",
    )

    # Connection Behavior Settings
    connection_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Timeout for connection attempts in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of retry attempts for failed operations",
    )
    retry_delay: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Base delay between retries in seconds (exponential backoff)",
    )

    # File Watcher Settings
    watch_enabled: bool = Field(
        default=False,
        description="Enable file watcher for automatic import",
    )
    watch_poll_interval: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Polling interval for file watcher in seconds",
    )
    watch_debounce_delay: float = Field(
        default=5.0,
        ge=1.0,
        le=60.0,
        description="Debounce delay to wait for file writes to complete",
    )

    # Health Check Settings
    health_check_interval: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Interval between automatic health checks in seconds",
    )
    health_check_timeout: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Timeout for health check operations in seconds",
    )

    @field_validator("csv_encoding")
    @classmethod
    def validate_encoding(cls, v: str) -> str:
        """Validate that the encoding is supported."""
        supported = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii", "iso-8859-1"]
        if v.lower() not in supported:
            raise ValueError(
                f"Unsupported encoding: {v}. Supported: {', '.join(supported)}"
            )
        return v.lower()

    @field_validator("csv_delimiter")
    @classmethod
    def validate_delimiter(cls, v: str) -> str:
        """Validate that the delimiter is a single character."""
        if len(v) != 1:
            raise ValueError(f"Delimiter must be a single character, got: '{v}'")
        return v

    @field_validator("db_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate that the port is in valid range."""
        if v < 1 or v > 65535:
            raise ValueError(f"Port must be between 1 and 65535, got: {v}")
        return v

    @property
    def is_database_configured(self) -> bool:
        """Check if database connection is fully configured."""
        return all([
            self.db_host,
            self.db_name,
            self.db_user,
            self.db_password,
        ])

    @property
    def is_csv_configured(self) -> bool:
        """Check if CSV import is configured."""
        return bool(self.csv_import_path)

    def get_connection_string(self) -> str:
        """
        Generate a masked connection string for logging.

        Returns:
            Connection string with password masked
        """
        if not self.is_database_configured:
            return "Not configured"

        return (
            f"mssql+pyodbc://{self.db_user}:****"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def to_safe_dict(self) -> dict:
        """
        Export configuration as dictionary with sensitive values masked.

        Returns:
            Dictionary representation with passwords masked
        """
        data = self.model_dump()
        if data.get("db_password"):
            data["db_password"] = "****"
        return data

    def __repr__(self) -> str:
        """Safe representation that doesn't expose passwords."""
        return (
            f"EpicorConfig("
            f"csv_path='{self.csv_import_path}', "
            f"db_host='{self.db_host}', "
            f"db_name='{self.db_name}', "
            f"db_user='{self.db_user}')"
        )
