"""
Base Connector Abstract Class

Defines the interface that all data connectors must implement.
This ensures consistent behavior across CSV and database connectors.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataConnector(ABC):
    """
    Abstract base class for all data connectors.

    Provides a consistent interface for fetching data from various sources
    including CSV files and direct database connections.

    All concrete implementations must implement the abstract methods defined here.
    """

    def __init__(self, connector_name: str = "BaseConnector"):
        """
        Initialize the base connector.

        Args:
            connector_name: Human-readable name for this connector instance
        """
        self.connector_name = connector_name
        self._connected = False
        self._last_health_check: Optional[datetime] = None
        self._connection_errors: List[str] = []

    @property
    def is_connected(self) -> bool:
        """Return current connection status."""
        return self._connected

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the data source.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            ConnectionError: If connection cannot be established
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close connection to the data source.

        Should be called when done with the connector to release resources.
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the connection.

        Returns:
            dict: Health check response with keys:
                - status: "healthy" | "unhealthy" | "degraded"
                - connection_type: "csv" | "database"
                - last_check: ISO timestamp
                - details: dict with additional info
                - errors: list of error messages
        """
        pass

    @abstractmethod
    def fetch_customers(self) -> List[Dict[str, Any]]:
        """
        Fetch customer master data.

        Returns:
            list: List of customer records as dictionaries

        Raises:
            DataFetchError: If data cannot be retrieved
        """
        pass

    @abstractmethod
    def fetch_invoices(self) -> List[Dict[str, Any]]:
        """
        Fetch open invoice/AR data.

        Returns:
            list: List of invoice records as dictionaries

        Raises:
            DataFetchError: If data cannot be retrieved
        """
        pass

    @abstractmethod
    def fetch_payments(self, since_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Fetch payment transaction data.

        Args:
            since_date: Optional filter to only get payments after this date

        Returns:
            list: List of payment records as dictionaries

        Raises:
            DataFetchError: If data cannot be retrieved
        """
        pass

    @abstractmethod
    def fetch_credit_status(self) -> List[Dict[str, Any]]:
        """
        Fetch credit limit and hold status data.

        Returns:
            list: List of credit status records as dictionaries

        Raises:
            DataFetchError: If data cannot be retrieved
        """
        pass

    def fetch_all(self, since_date: Optional[datetime] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch all data types in a single call.

        Args:
            since_date: Optional filter for payment data

        Returns:
            dict: Dictionary with keys 'customers', 'invoices', 'payments', 'credit_status'
        """
        logger.info(f"[{self.connector_name}] Fetching all data...")

        return {
            "customers": self.fetch_customers(),
            "invoices": self.fetch_invoices(),
            "payments": self.fetch_payments(since_date=since_date),
            "credit_status": self.fetch_credit_status(),
        }

    def _log_error(self, error_message: str) -> None:
        """Log an error and add it to the error list."""
        logger.error(f"[{self.connector_name}] {error_message}")
        self._connection_errors.append(error_message)
        # Keep only last 100 errors
        if len(self._connection_errors) > 100:
            self._connection_errors = self._connection_errors[-100:]

    def _clear_errors(self) -> None:
        """Clear the error list."""
        self._connection_errors = []

    def __enter__(self):
        """Context manager entry - establish connection."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.disconnect()
        return False


class DataFetchError(Exception):
    """Exception raised when data cannot be fetched from the source."""

    def __init__(self, message: str, source: str = "", original_error: Optional[Exception] = None):
        self.message = message
        self.source = source
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        error_str = f"DataFetchError: {self.message}"
        if self.source:
            error_str += f" (source: {self.source})"
        if self.original_error:
            error_str += f" - Original error: {str(self.original_error)}"
        return error_str


class ConnectionConfigError(Exception):
    """Exception raised when connector configuration is invalid."""
    pass
