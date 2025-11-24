"""
Customer Model - Customer Master Data
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, DateTime, func, Computed
from sqlalchemy.orm import relationship
from src.db.connection import Base
from decimal import Decimal
from typing import Optional


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    epicor_customer_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    dba_trade_name = Column(String(255))

    # Billing Address
    billing_address_line1 = Column(String(255))
    billing_address_line2 = Column(String(255))
    billing_city = Column(String(100))
    billing_state = Column(String(50))
    billing_zip = Column(String(20))

    # Contact Information
    billing_email = Column(String(255))
    billing_phone = Column(String(50))
    primary_contact_name = Column(String(255))

    # Sales Information
    salesperson_id = Column(String(50), index=True)
    salesperson_name = Column(String(255))

    # Credit Information
    terms_code = Column(String(20))
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)

    # Status
    status = Column(String(20), default="Active", index=True)  # Active, Inactive, On Hold, COD
    customer_type = Column(String(50))  # Contractor, Developer, DIY, etc.
    branch_id = Column(String(50), index=True)
    department = Column(String(100))

    # Tax Information
    tax_status = Column(String(20))
    tax_exempt_number = Column(String(50))

    # Activity Dates
    last_invoice_date = Column(Date, index=True)
    last_payment_date = Column(Date)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_synced_at = Column(DateTime)

    # Relationships
    invoices = relationship("Invoice", back_populates="customer", lazy="dynamic")
    payments = relationship("Payment", back_populates="customer", lazy="dynamic")
    notes = relationship("Note", back_populates="customer", lazy="dynamic")
    tasks = relationship("Task", back_populates="customer", lazy="dynamic")
    alerts = relationship("Alert", back_populates="customer", lazy="dynamic")
    disputes = relationship("Dispute", back_populates="customer", lazy="dynamic")
    credit_holds = relationship("CreditHold", back_populates="customer", lazy="dynamic")

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', status='{self.status}')>"

    @property
    def credit_utilization(self) -> float:
        """Calculate credit utilization percentage"""
        if self.credit_limit and self.credit_limit > 0:
            return float((self.current_balance or 0) / self.credit_limit * 100)
        return 0.0

    @property
    def is_over_credit_limit(self) -> bool:
        """Check if customer is over credit limit"""
        if self.credit_limit and self.credit_limit > 0:
            return (self.current_balance or 0) > self.credit_limit
        return False

    @property
    def is_near_credit_limit(self) -> bool:
        """Check if customer is near credit limit (>80%)"""
        return self.credit_utilization >= 80

    @property
    def days_since_last_invoice(self) -> Optional[int]:
        """Calculate days since last invoice"""
        if self.last_invoice_date:
            from datetime import date
            return (date.today() - self.last_invoice_date).days
        return None

    @property
    def is_inactive(self) -> bool:
        """Check if customer is inactive (no invoice in 90+ days)"""
        days = self.days_since_last_invoice
        return days is not None and days > 90

    @property
    def display_address(self) -> str:
        """Format full billing address"""
        parts = [
            self.billing_address_line1,
            self.billing_address_line2,
            f"{self.billing_city}, {self.billing_state} {self.billing_zip}"
            if self.billing_city else None
        ]
        return "\n".join(p for p in parts if p)
