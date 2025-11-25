"""
Dispute Model - Invoice Dispute Tracking
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.db.connection import Base


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)

    # Dispute Details
    reason_code = Column(String(50), index=True)  # pricing, damaged, short_ship, wrong_item, tax, duplicate, other
    description = Column(Text)
    disputed_amount = Column(Numeric(15, 2))
    status = Column(String(20), default="Open", index=True)  # Open, In Review, Resolved, Rejected
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)
    resolution_note = Column(Text)

    # Relationships
    customer = relationship("Customer", back_populates="disputes")
    invoice = relationship("Invoice", back_populates="disputes")
    attachments = relationship("DisputeAttachment", back_populates="dispute", cascade="all, delete-orphan")
    history = relationship("DisputeHistory", back_populates="dispute", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dispute(id={self.id}, reason='{self.reason_code}', status='{self.status}')>"

    @property
    def is_open(self) -> bool:
        return self.status in ["Open", "In Review"]

    @property
    def days_open(self) -> int:
        from datetime import datetime
        return (datetime.now() - self.created_at).days if self.created_at else 0
