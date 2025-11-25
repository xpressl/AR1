"""
Email Template Model

Stores reusable email templates for customer communications
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.db.connection import Base


class EmailTemplate(Base):
    """Email template for standardized customer communications."""

    __tablename__ = "email_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Template information
    name = Column(String(200), nullable=False)
    subject = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)

    # Template categorization
    template_type = Column(String(50), nullable=False)  # payment_reminder, dispute_ack, etc.
    category = Column(String(50))  # collections, disputes, general

    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Default template for this type

    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Template variables (stored as JSON or comma-separated)
    available_variables = Column(Text)  # e.g., "customer_name,balance,invoice_number,due_date"

    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)

    # Relationships
    creator = relationship("User")
    usage_logs = relationship("TemplateUsageLog", back_populates="template")

    def __repr__(self):
        return f"<EmailTemplate(id={self.id}, name='{self.name}', type='{self.template_type}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "subject": self.subject,
            "body": self.body,
            "template_type": self.template_type,
            "category": self.category,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "available_variables": self.available_variables,
            "usage_count": self.usage_count,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None
        }
