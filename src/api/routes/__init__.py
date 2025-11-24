"""
AR Control Hub - API Routes
"""
from src.api.routes import customers, invoices, payments, notes, alerts, tasks, auth, dashboard, reports

__all__ = [
    "customers",
    "invoices",
    "payments",
    "notes",
    "alerts",
    "tasks",
    "auth",
    "dashboard",
    "reports"
]
