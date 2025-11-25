"""
Dispute Attachment Model

Handles file attachments for disputes (invoices, proof of delivery, correspondence, etc.)
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.db.base import Base


class DisputeAttachment(Base):
    """File attachment for a dispute."""

    __tablename__ = "dispute_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False)

    # File information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    file_type = Column(String(50))  # MIME type (e.g., application/pdf)

    # Metadata
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(String(500))

    # Relationships
    dispute = relationship("Dispute", back_populates="attachments")
    uploader = relationship("User")

    def __repr__(self):
        return f"<DisputeAttachment(id={self.id}, dispute_id={self.dispute_id}, file_name='{self.file_name}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "dispute_id": str(self.dispute_id),
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "uploaded_by": str(self.uploaded_by) if self.uploaded_by else None,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "description": self.description
        }
