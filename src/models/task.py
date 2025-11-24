"""
Task Model - Collection Tasks and Follow-ups
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.db.connection import Base
from datetime import datetime


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Task Details
    task_type = Column(String(30), nullable=False)  # collection_call, follow_up, dispute_resolution, review
    description = Column(Text)
    due_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime)
    status = Column(String(20), default="Open", index=True)  # Open, Completed, Canceled, Snoozed
    priority = Column(Integer, default=5)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="tasks")
    assigned_user = relationship("User", back_populates="tasks_assigned")

    def __repr__(self):
        return f"<Task(id={self.id}, type='{self.task_type}', status='{self.status}')>"

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        return self.status == "Open" and self.due_at < datetime.now()

    @property
    def is_due_today(self) -> bool:
        """Check if task is due today"""
        return self.due_at.date() == datetime.now().date()
