"""
Dispute History Model

Audit trail for dispute status changes and modifications
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.db.base import Base


class DisputeHistory(Base):
    """Audit trail for dispute changes."""

    __tablename__ = "dispute_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False)

    # Change information
    action = Column(String(100), nullable=False)  # created, status_changed, assigned, resolved, etc.
    old_value = Column(Text)
    new_value = Column(Text)
    comment = Column(Text)

    # Metadata
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    dispute = relationship("Dispute", back_populates="history")
    user = relationship("User")

    def __repr__(self):
        return f"<DisputeHistory(id={self.id}, dispute_id={self.dispute_id}, action='{self.action}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "dispute_id": str(self.dispute_id),
            "action": self.action,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "comment": self.comment,
            "changed_by": str(self.changed_by) if self.changed_by else None,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None
        }
