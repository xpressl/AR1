"""
CreditHold Model - Credit Hold History
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.db.connection import Base


class CreditHold(Base):
    __tablename__ = "credit_holds"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Hold Details
    placed_at = Column(DateTime, server_default=func.now())
    placed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason_code = Column(String(50))
    reason_note = Column(Text)

    # Release Details
    released_at = Column(DateTime)
    released_by_user_id = Column(Integer, ForeignKey("users.id"))
    release_note = Column(Text)

    # Relationships
    customer = relationship("Customer", back_populates="credit_holds")

    def __repr__(self):
        return f"<CreditHold(id={self.id}, customer_id={self.customer_id}, reason='{self.reason_code}')>"

    @property
    def is_active(self) -> bool:
        return self.released_at is None

    @property
    def days_on_hold(self) -> int:
        from datetime import datetime
        end = self.released_at or datetime.now()
        return (end - self.placed_at).days if self.placed_at else 0
