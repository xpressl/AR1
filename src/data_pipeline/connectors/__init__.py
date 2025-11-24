"""
Data Connectors Module

Provides abstract base class and concrete implementations for
connecting to Epicor data sources.
"""

from .base_connector import DataConnector
from .csv_connector import CSVConnector
from .db_connector import DatabaseConnector
from .connector_factory import ConnectorFactory

__all__ = [
    "DataConnector",
    "CSVConnector",
    "DatabaseConnector",
    "ConnectorFactory",
]
