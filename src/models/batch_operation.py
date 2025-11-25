"""
Batch Operation Model

Tracks bulk operations performed on multiple records
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.db.base import Base


class BatchOperation(Base):
    """Tracks batch/bulk operations."""

    __tablename__ = "batch_operations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Operation details
    operation_type = Column(String(100), nullable=False)  # send_emails, assign_tasks, update_status, etc.
    description = Column(String(500))

    # Record counts
    total_records = Column(Integer, nullable=False)
    processed_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)

    # Status
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed, cancelled

    # Metadata
    initiated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)

    # Results and errors
    error_log = Column(Text)  # JSON array of errors
    result_summary = Column(Text)  # JSON summary of results

    # Relationships
    initiator = relationship("User")

    def __repr__(self):
        return f"<BatchOperation(id={self.id}, type='{self.operation_type}', status='{self.status}')>"

    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.total_records == 0:
            return 0
        return (self.processed_records / self.total_records) * 100

    @property
    def success_rate(self):
        """Calculate success rate."""
        if self.processed_records == 0:
            return 0
        return (self.successful_records / self.processed_records) * 100

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "operation_type": self.operation_type,
            "description": self.description,
            "total_records": self.total_records,
            "processed_records": self.processed_records,
            "successful_records": self.successful_records,
            "failed_records": self.failed_records,
            "status": self.status,
            "progress_percentage": self.progress_percentage,
            "success_rate": self.success_rate,
            "initiated_by": str(self.initiated_by),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_log": self.error_log,
            "result_summary": self.result_summary
        }
