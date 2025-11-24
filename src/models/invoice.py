"""
Invoice Model - AR Open Items
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.db.connection import Base
from datetime import date
from typing import Optional


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    epicor_invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Invoice Details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    original_amount = Column(Numeric(15, 2), nullable=False)
    open_balance = Column(Numeric(15, 2), nullable=False)

    # Status
    status = Column(String(20), default="Open", index=True)  # Open, Paid, Partial, Disputed, Written Off
    invoice_type = Column(String(20), default="Invoice")  # Invoice, Credit Memo, Finance Charge

    # Classification
    branch_id = Column(String(50))
    department = Column(String(100))
    salesperson_id = Column(String(50))

    # References
    job_reference = Column(String(100))
    po_reference = Column(String(100))
    project_reference = Column(String(100))
    order_number = Column(String(50))
    ticket_number = Column(String(50))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_synced_at = Column(DateTime)

    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    payment_applications = relationship("PaymentApplication", back_populates="invoice", lazy="dynamic")
    notes = relationship("Note", back_populates="invoice", lazy="dynamic")
    alerts = relationship("Alert", back_populates="invoice", lazy="dynamic")
    disputes = relationship("Dispute", back_populates="invoice", lazy="dynamic")

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.epicor_invoice_number}', balance={self.open_balance})>"

    @property
    def days_past_due(self) -> int:
        """Calculate days past due"""
        if self.due_date:
            days = (date.today() - self.due_date).days
            return max(0, days)
        return 0

    @property
    def aging_bucket(self) -> str:
        """Determine aging bucket"""
        days = self.days_past_due
        if days == 0 and self.due_date >= date.today():
            return "Current"
        elif days <= 30:
            return "1-30"
        elif days <= 60:
            return "31-60"
        elif days <= 90:
            return "61-90"
        else:
            return "90+"

    @property
    def is_past_due(self) -> bool:
        """Check if invoice is past due"""
        return self.days_past_due > 0

    @property
    def is_critically_overdue(self) -> bool:
        """Check if invoice is 90+ days past due"""
        return self.days_past_due >= 90

    @property
    def amount_paid(self) -> float:
        """Calculate amount paid on this invoice"""
        return float(self.original_amount - self.open_balance)
