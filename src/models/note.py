"""
Note Model - Collection Notes and Promise to Pay
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.db.connection import Base
from datetime import date


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Note Details
    note_type = Column(String(30), nullable=False, index=True)  # call, email, dispute, internal, promise_to_pay
    content = Column(Text, nullable=False)

    # Promise to Pay Fields
    promise_amount = Column(Numeric(15, 2))
    promise_date = Column(Date)
    promise_status = Column(String(20))  # pending, kept, broken

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="notes")
    invoice = relationship("Invoice", back_populates="notes")
    user = relationship("User", back_populates="notes")

    def __repr__(self):
        return f"<Note(id={self.id}, type='{self.note_type}', customer_id={self.customer_id})>"

    @property
    def is_promise(self) -> bool:
        """Check if note is a promise to pay"""
        return self.note_type == "promise_to_pay"

    @property
    def is_promise_due(self) -> bool:
        """Check if promise date has passed"""
        if self.promise_date:
            return self.promise_date < date.today()
        return False

    @property
    def is_promise_broken(self) -> bool:
        """Check if promise is broken"""
        return self.promise_status == "broken"
