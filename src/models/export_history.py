"""
Export History Model

Tracks data exports for audit and reuse
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.db.base import Base


class ExportHistory(Base):
    """History of data exports."""

    __tablename__ = "export_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Export details
    export_type = Column(String(100), nullable=False)  # customers, invoices, aging_report, etc.
    export_name = Column(String(200))  # User-friendly name
    file_format = Column(String(20), nullable=False)  # xlsx, pdf, csv

    # File information
    file_path = Column(String(500))  # Path to generated file
    file_size = Column(Integer)  # Size in bytes
    record_count = Column(Integer)  # Number of records exported

    # Query parameters (stored as JSON)
    filters = Column(JSONB)  # Filters applied to the export

    # Metadata
    exported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exported_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Status
    status = Column(String(50), default="completed")  # pending, completed, failed, expired
    expires_at = Column(DateTime)  # When the file should be auto-deleted

    # Relationships
    exporter = relationship("User")

    def __repr__(self):
        return f"<ExportHistory(id={self.id}, type='{self.export_type}', format='{self.file_format}')>"

    @property
    def is_expired(self):
        """Check if export file has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "export_type": self.export_type,
            "export_name": self.export_name,
            "file_format": self.file_format,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "record_count": self.record_count,
            "filters": self.filters,
            "exported_by": str(self.exported_by),
            "exported_at": self.exported_at.isoformat() if self.exported_at else None,
            "status": self.status,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired
        }
