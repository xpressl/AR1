"""
ImportRun Model - Epicor Data Sync Tracking
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from src.db.connection import Base


class ImportRun(Base):
    __tablename__ = "import_runs"

    id = Column(Integer, primary_key=True, index=True)

    # Timing
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    finished_at = Column(DateTime)

    # Status
    status = Column(String(20), default="Running", index=True)  # Running, Success, Failed, Partial
    error_message = Column(Text)

    # Statistics
    customers_imported = Column(Integer, default=0)
    customers_updated = Column(Integer, default=0)
    invoices_imported = Column(Integer, default=0)
    invoices_updated = Column(Integer, default=0)
    payments_imported = Column(Integer, default=0)
    alerts_generated = Column(Integer, default=0)
    alerts_resolved = Column(Integer, default=0)

    def __repr__(self):
        return f"<ImportRun(id={self.id}, status='{self.status}', started_at='{self.started_at}')>"

    @property
    def duration_seconds(self) -> int:
        if self.finished_at and self.started_at:
            return int((self.finished_at - self.started_at).total_seconds())
        return 0

    @property
    def is_running(self) -> bool:
        return self.status == "Running"

    @property
    def is_successful(self) -> bool:
        return self.status == "Success"
