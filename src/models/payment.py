"""
Payment and PaymentApplication Models
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.db.connection import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    epicor_payment_id = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Payment Details
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_type = Column(String(20))  # Check, ACH, Card, Cash, Wire
    check_number = Column(String(50))
    reference_number = Column(String(100))
    unapplied_amount = Column(Numeric(15, 2), default=0)
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    last_synced_at = Column(DateTime)

    # Relationships
    customer = relationship("Customer", back_populates="payments")
    applications = relationship("PaymentApplication", back_populates="payment", lazy="dynamic")

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, type='{self.payment_type}')>"

    @property
    def applied_amount(self) -> float:
        """Calculate total applied amount"""
        return float(self.amount - (self.unapplied_amount or 0))

    @property
    def is_fully_applied(self) -> bool:
        """Check if payment is fully applied"""
        return (self.unapplied_amount or 0) == 0


class PaymentApplication(Base):
    __tablename__ = "payment_applications"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    amount_applied = Column(Numeric(15, 2), nullable=False)
    applied_at = Column(DateTime, server_default=func.now())

    # Relationships
    payment = relationship("Payment", back_populates="applications")
    invoice = relationship("Invoice", back_populates="payment_applications")

    def __repr__(self):
        return f"<PaymentApplication(payment_id={self.payment_id}, invoice_id={self.invoice_id}, amount={self.amount_applied})>"
