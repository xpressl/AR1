"""
EmailLog Model - Email Communication Tracking
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.db.connection import Base


class EmailLog(Base):
    __tablename__ = "email_log"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    # Email Details
    email_type = Column(String(30), nullable=False, index=True)  # statement, reminder, notice, custom
    template_used = Column(String(50))
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(255))
    body = Column(Text)

    # Status
    sent_at = Column(DateTime, server_default=func.now())
    sent_by_user_id = Column(Integer, ForeignKey("users.id"))
    delivery_status = Column(String(20), default="sent")  # sent, delivered, bounced, failed
    opened_at = Column(DateTime)

    def __repr__(self):
        return f"<EmailLog(id={self.id}, type='{self.email_type}', status='{self.delivery_status}')>"
