"""
Configuration Module for Data Pipeline

Provides configuration management for Epicor connectors
and field mappings for data transformation.
"""

from .epicor_config import EpicorConfig
from .field_mappings import FieldMappings

__all__ = [
    "EpicorConfig",
    "FieldMappings",
]
