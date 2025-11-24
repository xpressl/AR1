"""
Notification Model - In-App Notifications
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.db.connection import Base


class Notification(Base):
    """In-app notification database model."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Notification details
    notification_type = Column(String(50), nullable=False)  # alert, task, promise, system
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    severity = Column(String(20), default="info")  # info, warning, critical

    # Related entities
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    # Action link
    action_url = Column(String(500), nullable=True)

    # Status
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)
    is_dismissed = Column(Boolean, default=False)
    dismissed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="notifications")
    customer = relationship("Customer", backref="notifications")

    def __repr__(self):
        return f"<Notification {self.id} type={self.notification_type} read={self.is_read}>"

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()

    def dismiss(self):
        self.is_dismissed = True
        self.dismissed_at = datetime.utcnow()
