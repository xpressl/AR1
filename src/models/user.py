"""
User Model - Authentication and RBAC
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from src.db.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(30), nullable=False)  # ar_specialist, ar_manager, sales_rep, inside_sales, owner, admin
    branch_id = Column(String(50))
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    notes = relationship("Note", back_populates="user", foreign_keys="Note.user_id")
    tasks_assigned = relationship("Task", back_populates="assigned_user", foreign_keys="Task.assigned_to_user_id")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    @property
    def is_manager(self) -> bool:
        return self.role in ["ar_manager", "owner", "admin"]

    @property
    def can_approve_writeoffs(self) -> bool:
        return self.role in ["ar_manager", "owner", "admin"]

    @property
    def can_modify_credit_limits(self) -> bool:
        return self.role in ["ar_manager", "owner", "admin"]
