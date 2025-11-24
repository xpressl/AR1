"""
Credit Limit Detector - A03
Detects customers near or over their credit limit.
"""
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.customer import Customer


class CreditLimitDetector:
    """
    Detects customers who are near (80%+) or over their credit limit.
    """

    def __init__(self, db: AsyncSession, near_threshold: float = 80):
        self.db = db
        self.near_threshold = near_threshold

    async def detect_over_limit(self) -> List[Dict]:
        """Find customers over credit limit"""
        result = await self.db.execute(
            select(Customer)
            .where(Customer.credit_limit > 0)
            .where(Customer.current_balance > 0)
        )
        customers = result.scalars().all()

        over_limit = []
        for c in customers:
            if c.is_over_credit_limit:
                over_limit.append({
                    "customer_id": c.id,
                    "customer_name": c.name,
                    "credit_limit": float(c.credit_limit),
                    "current_balance": float(c.current_balance),
                    "over_by": float(c.current_balance - c.credit_limit),
                    "utilization": c.credit_utilization,
                    "salesperson": c.salesperson_name,
                    "status": c.status
                })

        over_limit.sort(key=lambda x: x["over_by"], reverse=True)
        return over_limit

    async def detect_near_limit(self) -> List[Dict]:
        """Find customers near credit limit (80%+)"""
        result = await self.db.execute(
            select(Customer)
            .where(Customer.credit_limit > 0)
            .where(Customer.current_balance > 0)
        )
        customers = result.scalars().all()

        near_limit = []
        for c in customers:
            if c.is_near_credit_limit and not c.is_over_credit_limit:
                near_limit.append({
                    "customer_id": c.id,
                    "customer_name": c.name,
                    "credit_limit": float(c.credit_limit),
                    "current_balance": float(c.current_balance),
                    "available": float(c.credit_limit - c.current_balance),
                    "utilization": c.credit_utilization,
                    "salesperson": c.salesperson_name
                })

        near_limit.sort(key=lambda x: x["utilization"], reverse=True)
        return near_limit

    async def get_summary(self) -> Dict:
        """Get summary of credit limit issues"""
        over = await self.detect_over_limit()
        near = await self.detect_near_limit()

        return {
            "over_limit": {
                "count": len(over),
                "total_over_by": sum(c["over_by"] for c in over),
                "customers": over[:10]
            },
            "near_limit": {
                "count": len(near),
                "customers": near[:10]
            }
        }
