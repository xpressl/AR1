"""
Alert Model - System-Generated Risk Alerts
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.db.connection import Base
from enum import Enum


class AlertType(str, Enum):
    """Alert type enumeration"""
    INACTIVE_BUT_OWING = "inactive_but_owing"
    NEAR_CREDIT_LIMIT = "near_credit_limit"
    OVER_CREDIT_LIMIT = "over_credit_limit"
    LONG_OVERDUE_60 = "long_overdue_60"
    LONG_OVERDUE_90 = "long_overdue_90"
    BROKEN_PROMISE = "broken_promise"
    UNAPPLIED_CREDITS = "unapplied_credits"
    CREDIT_HOLD = "credit_hold"
    PAYMENT_PATTERN = "payment_pattern"
    HIGH_BALANCE = "high_balance"
    DISPUTE_OPEN = "dispute_open"
    PROMISE_DUE = "promise_due"


class AlertSeverity(str, Enum):
    """Alert severity enumeration"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)

    # Alert Details
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)  # Low, Medium, High, Critical
    is_active = Column(Boolean, default=True, index=True)
    message = Column(Text)

    # Timestamps
    triggered_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)
    resolved_by_user_id = Column(Integer, ForeignKey("users.id"))
    resolution_note = Column(Text)

    # Relationships
    customer = relationship("Customer", back_populates="alerts")
    invoice = relationship("Invoice", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"

    @property
    def is_critical(self) -> bool:
        """Check if alert is critical (should blink)"""
        return self.severity == AlertSeverity.CRITICAL.value

    @property
    def requires_immediate_action(self) -> bool:
        """Check if alert requires immediate action"""
        return self.severity in [AlertSeverity.CRITICAL.value, AlertSeverity.HIGH.value]

    @property
    def css_class(self) -> str:
        """Return CSS class for styling"""
        severity_classes = {
            "Critical": "alert-critical-pulse",
            "High": "alert-high",
            "Medium": "alert-medium",
            "Low": "alert-low"
        }
        return severity_classes.get(self.severity, "alert-low")

    @property
    def icon(self) -> str:
        """Return icon for alert type"""
        icons = {
            "inactive_but_owing": "user-x",
            "near_credit_limit": "alert-triangle",
            "over_credit_limit": "alert-octagon",
            "long_overdue_60": "clock",
            "long_overdue_90": "clock",
            "broken_promise": "x-circle",
            "unapplied_credits": "credit-card",
            "credit_hold": "lock",
            "payment_pattern": "trending-down",
            "high_balance": "dollar-sign",
            "dispute_open": "message-circle",
            "promise_due": "calendar"
        }
        return icons.get(self.alert_type, "alert-circle")

    @classmethod
    def get_severity_for_inactive(cls, days_inactive: int) -> str:
        """Determine severity based on days inactive"""
        if days_inactive > 180:
            return AlertSeverity.CRITICAL.value
        elif days_inactive > 120:
            return AlertSeverity.HIGH.value
        elif days_inactive > 90:
            return AlertSeverity.MEDIUM.value
        return AlertSeverity.LOW.value

    @classmethod
    def get_severity_for_overdue(cls, days_past_due: int) -> str:
        """Determine severity based on days past due"""
        if days_past_due >= 90:
            return AlertSeverity.CRITICAL.value
        elif days_past_due >= 60:
            return AlertSeverity.HIGH.value
        elif days_past_due >= 30:
            return AlertSeverity.MEDIUM.value
        return AlertSeverity.LOW.value
