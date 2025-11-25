"""
Template Usage Log Model

Tracks email template usage and engagement metrics
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.db.connection import Base


class TemplateUsageLog(Base):
    """Log of email template usage and engagement."""

    __tablename__ = "template_usage_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    template_id = Column(UUID(as_uuid=True), ForeignKey("email_templates.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"))
    sent_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Timestamps
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)

    # Status
    status = Column(String(50), default="sent")  # sent, delivered, opened, clicked, bounced, failed

    # Email details
    recipient_email = Column(String(200))
    subject_rendered = Column(String(300))  # Subject after variable substitution
    email_log_id = Column(UUID(as_uuid=True), ForeignKey("email_logs.id"))

    # Relationships
    template = relationship("EmailTemplate", back_populates="usage_logs")
    customer = relationship("Customer")
    sender = relationship("User")
    email_log = relationship("EmailLog")

    def __repr__(self):
        return f"<TemplateUsageLog(id={self.id}, template_id={self.template_id}, status='{self.status}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "template_id": str(self.template_id),
            "customer_id": str(self.customer_id) if self.customer_id else None,
            "sent_by": str(self.sent_by) if self.sent_by else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "clicked_at": self.clicked_at.isoformat() if self.clicked_at else None,
            "status": self.status,
            "recipient_email": self.recipient_email,
            "subject_rendered": self.subject_rendered
        }
