"""
Inactive Account Detector - A02
Specialized detector for finding inactive customers with outstanding balances.
"""
from datetime import date
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.customer import Customer
from src.models.alert import AlertSeverity


class InactiveAccountDetector:
    """
    Detects customers who haven't purchased in configurable days
    but still have outstanding balance.
    """

    def __init__(
        self,
        db: AsyncSession,
        inactive_days_threshold: int = 90,
        balance_threshold: float = 100
    ):
        self.db = db
        self.inactive_days = inactive_days_threshold
        self.balance_threshold = balance_threshold

    async def detect(self) -> List[Dict]:
        """
        Find all inactive customers with balance.
        Returns list of customer data with severity.
        """
        result = await self.db.execute(
            select(Customer)
            .where(Customer.current_balance > self.balance_threshold)
            .where(Customer.status == "Active")
        )
        customers = result.scalars().all()

        inactive_accounts = []
        for customer in customers:
            days_inactive = customer.days_since_last_invoice
            if days_inactive is None or days_inactive < self.inactive_days:
                continue

            severity = self._calculate_severity(days_inactive)

            inactive_accounts.append({
                "customer_id": customer.id,
                "customer_name": customer.name,
                "days_inactive": days_inactive,
                "balance": float(customer.current_balance),
                "severity": severity,
                "last_invoice_date": customer.last_invoice_date.isoformat() if customer.last_invoice_date else None,
                "salesperson": customer.salesperson_name,
                "branch": customer.branch_id
            })

        # Sort by days inactive (most inactive first)
        inactive_accounts.sort(key=lambda x: x["days_inactive"], reverse=True)
        return inactive_accounts

    def _calculate_severity(self, days_inactive: int) -> str:
        """Calculate severity based on days inactive"""
        if days_inactive > 180:
            return AlertSeverity.CRITICAL.value
        elif days_inactive > 120:
            return AlertSeverity.HIGH.value
        elif days_inactive > 90:
            return AlertSeverity.MEDIUM.value
        return AlertSeverity.LOW.value

    async def get_summary(self) -> Dict:
        """Get summary of inactive accounts"""
        accounts = await self.detect()

        by_severity = {
            "Critical": [],
            "High": [],
            "Medium": [],
            "Low": []
        }

        total_balance = 0
        for acc in accounts:
            by_severity[acc["severity"]].append(acc)
            total_balance += acc["balance"]

        return {
            "total_count": len(accounts),
            "total_balance": total_balance,
            "by_severity": {
                k: {"count": len(v), "balance": sum(a["balance"] for a in v)}
                for k, v in by_severity.items()
            },
            "top_10": accounts[:10]
        }
