"""
Connector Factory

Factory class for creating and managing data connectors.
Provides a centralized way to instantiate the appropriate connector
based on configuration or explicit selection.
"""

from enum import Enum
from typing import Optional
import logging

from .base_connector import DataConnector, ConnectionConfigError
from .csv_connector import CSVConnector
from .db_connector import DatabaseConnector
from ..config.epicor_config import EpicorConfig

logger = logging.getLogger(__name__)


class ConnectorType(Enum):
    """Enumeration of available connector types."""
    CSV = "csv"
    DATABASE = "database"
    AUTO = "auto"


class ConnectorFactory:
    """
    Factory for creating data connectors.

    This factory handles the creation of the appropriate connector
    based on configuration and availability. It can also manage
    fallback behavior when the primary connector is unavailable.

    Usage:
        # Create CSV connector
        connector = ConnectorFactory.create(ConnectorType.CSV)

        # Auto-detect based on config
        connector = ConnectorFactory.create(ConnectorType.AUTO, config)

        # With fallback
        connector = ConnectorFactory.create_with_fallback(config)
    """

    @staticmethod
    def create(
        connector_type: ConnectorType,
        config: Optional[EpicorConfig] = None,
    ) -> DataConnector:
        """
        Create a data connector of the specified type.

        Args:
            connector_type: Type of connector to create
            config: Optional configuration object

        Returns:
            DataConnector instance

        Raises:
            ValueError: If connector type is invalid
            ConnectionConfigError: If configuration is invalid for the connector
        """
        config = config or EpicorConfig()

        if connector_type == ConnectorType.CSV:
            logger.info("Creating CSV connector")
            return CSVConnector(config)

        elif connector_type == ConnectorType.DATABASE:
            logger.info("Creating database connector")
            return DatabaseConnector(config)

        elif connector_type == ConnectorType.AUTO:
            return ConnectorFactory._auto_select_connector(config)

        else:
            raise ValueError(f"Unknown connector type: {connector_type}")

    @staticmethod
    def _auto_select_connector(config: EpicorConfig) -> DataConnector:
        """
        Automatically select the best available connector based on config.

        Priority:
        1. Database connector (if fully configured)
        2. CSV connector (fallback)

        Args:
            config: Configuration object

        Returns:
            DataConnector instance
        """
        # Check if database is configured
        if (
            config.db_host
            and config.db_name
            and config.db_user
            and config.db_password
        ):
            logger.info("Database configuration found, selecting database connector")
            return DatabaseConnector(config)

        # Fall back to CSV
        logger.info("No database configuration, selecting CSV connector")
        return CSVConnector(config)

    @staticmethod
    def create_with_fallback(
        config: Optional[EpicorConfig] = None,
        primary: ConnectorType = ConnectorType.DATABASE,
    ) -> DataConnector:
        """
        Create a connector with automatic fallback to CSV if primary fails.

        Attempts to create and connect to the primary connector.
        If that fails, falls back to CSV connector.

        Args:
            config: Optional configuration object
            primary: Primary connector type to try first

        Returns:
            Connected DataConnector instance

        Raises:
            ConnectionConfigError: If both primary and fallback fail
        """
        config = config or EpicorConfig()

        # Try primary connector
        if primary == ConnectorType.DATABASE:
            try:
                connector = DatabaseConnector(config)
                connector.connect()
                logger.info("Successfully connected using primary database connector")
                return connector
            except (ConnectionConfigError, Exception) as e:
                logger.warning(
                    f"Primary database connector failed: {e}. "
                    f"Falling back to CSV connector."
                )

        # Try CSV connector as fallback
        try:
            connector = CSVConnector(config)
            connector.connect()
            logger.info("Successfully connected using CSV connector (fallback)")
            return connector
        except ConnectionConfigError as e:
            raise ConnectionConfigError(
                f"All connectors failed. Last error: {e}"
            ) from e

    @staticmethod
    def get_available_types() -> list[ConnectorType]:
        """
        Get list of all available connector types.

        Returns:
            List of ConnectorType values
        """
        return [ConnectorType.CSV, ConnectorType.DATABASE]

    @staticmethod
    def validate_config(
        connector_type: ConnectorType,
        config: Optional[EpicorConfig] = None,
    ) -> dict:
        """
        Validate configuration for a specific connector type.

        Args:
            connector_type: Type of connector to validate for
            config: Configuration to validate

        Returns:
            dict with keys:
                - valid: bool indicating if config is valid
                - errors: list of error messages
                - warnings: list of warning messages
        """
        config = config or EpicorConfig()
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        if connector_type == ConnectorType.CSV:
            # Validate CSV configuration
            if not config.csv_import_path:
                result["errors"].append("csv_import_path is not set")
                result["valid"] = False

            if config.csv_encoding not in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
                result["warnings"].append(
                    f"Unusual CSV encoding: {config.csv_encoding}"
                )

        elif connector_type == ConnectorType.DATABASE:
            # Validate database configuration
            required = {
                "db_host": config.db_host,
                "db_name": config.db_name,
                "db_user": config.db_user,
                "db_password": config.db_password,
            }

            for field, value in required.items():
                if not value:
                    result["errors"].append(f"{field} is not set")
                    result["valid"] = False

            if config.db_port <= 0 or config.db_port > 65535:
                result["errors"].append(
                    f"Invalid database port: {config.db_port}"
                )
                result["valid"] = False

        return result
