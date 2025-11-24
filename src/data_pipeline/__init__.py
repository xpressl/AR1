"""
Data Pipeline Module for AR Control Hub

This module provides data connectors and import functionality for
integrating with Epicor Eagle ERP system.

Supported data sources:
- CSV file exports from Epicor
- Direct database connections (read-only)

Components:
- connectors: Data source connectors (CSV, Database)
- config: Configuration management
- health: Connection health monitoring
- watchers: File system monitoring for new imports
"""

from .connectors import (
    DataConnector,
    CSVConnector,
    DatabaseConnector,
    ConnectorFactory,
)
from .config import EpicorConfig
from .health import ConnectionHealthService

__version__ = "1.0.0"
__all__ = [
    "DataConnector",
    "CSVConnector",
    "DatabaseConnector",
    "ConnectorFactory",
    "EpicorConfig",
    "ConnectionHealthService",
]
