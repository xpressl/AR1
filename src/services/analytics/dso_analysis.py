"""
DSO Analysis Service - R02
Calculates and trends Days Sales Outstanding metrics.
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case, extract
import logging

from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.payment import Payment

logger = logging.getLogger(__name__)


class DSOAnalysisService:
    """
    Calculates Days Sales Outstanding (DSO) metrics and trends.
    DSO = (Accounts Receivable / Total Credit Sales) * Number of Days
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_current_dso(self) -> Dict:
        """
        Calculate current DSO using the Countback Method.
        More accurate for businesses with varying sales.
        """
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)
        sixty_days_ago = today - timedelta(days=60)
        ninety_days_ago = today - timedelta(days=90)

        # Get current AR balance
        ar_result = await self.db.execute(
            select(func.sum(Invoice.open_balance)).where(
                Invoice.open_balance > 0
            )
        )
        total_ar = float(ar_result.scalar() or 0)

        # Get sales for different periods (using invoice original amounts as proxy)
        sales_30 = await self._get_sales_for_period(thirty_days_ago, today)
        sales_60 = await self._get_sales_for_period(sixty_days_ago, today)
        sales_90 = await self._get_sales_for_period(ninety_days_ago, today)

        # Calculate DSO using average daily sales
        avg_daily_sales_30 = sales_30 / 30 if sales_30 > 0 else 0
        avg_daily_sales_60 = sales_60 / 60 if sales_60 > 0 else 0
        avg_daily_sales_90 = sales_90 / 90 if sales_90 > 0 else 0

        dso_30 = round(total_ar / avg_daily_sales_30) if avg_daily_sales_30 > 0 else 0
        dso_60 = round(total_ar / avg_daily_sales_60) if avg_daily_sales_60 > 0 else 0
        dso_90 = round(total_ar / avg_daily_sales_90) if avg_daily_sales_90 > 0 else 0

        # Use 90-day average as primary DSO
        primary_dso = dso_90

        # Get target DSO (could be from config)
        target_dso = 35  # Industry standard for building supplies

        return {
            "as_of_date": today.isoformat(),
            "total_ar": total_ar,
            "dso": {
                "current": primary_dso,
                "30_day_basis": dso_30,
                "60_day_basis": dso_60,
                "90_day_basis": dso_90
            },
            "target_dso": target_dso,
            "variance_from_target": primary_dso - target_dso,
            "status": "above_target" if primary_dso > target_dso else "on_target",
            "daily_sales_avg": {
                "30_day": avg_daily_sales_30,
                "60_day": avg_daily_sales_60,
                "90_day": avg_daily_sales_90
            }
        }

    async def _get_sales_for_period(self, start_date: date, end_date: date) -> float:
        """Get total sales (invoiced amount) for a period."""
        result = await self.db.execute(
            select(func.sum(Invoice.original_amount)).where(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= end_date
            )
        )
        return float(result.scalar() or 0)

    async def get_dso_trend(self, months: int = 12) -> List[Dict]:
        """
        Get monthly DSO trend for the specified number of months.
        """
        today = date.today()
        trends = []

        for month_offset in range(months, 0, -1):
            # Calculate month boundaries
            target_date = today - timedelta(days=month_offset * 30)
            month_start = target_date.replace(day=1)

            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

            # Get AR as of month end
            ar_result = await self.db.execute(
                select(func.sum(Invoice.open_balance)).where(
                    Invoice.invoice_date <= month_end
                )
            )
            # Simplified - in production, you'd snapshot AR at month end
            ar_at_month_end = float(ar_result.scalar() or 0)

            # Get sales for that month
            sales_result = await self.db.execute(
                select(func.sum(Invoice.original_amount)).where(
                    Invoice.invoice_date >= month_start,
                    Invoice.invoice_date <= month_end
                )
            )
            monthly_sales = float(sales_result.scalar() or 0)

            # Calculate DSO
            days_in_month = (month_end - month_start).days + 1
            avg_daily_sales = monthly_sales / days_in_month if monthly_sales > 0 else 0
            dso = round(ar_at_month_end / avg_daily_sales) if avg_daily_sales > 0 else 0

            trends.append({
                "month": month_start.strftime("%Y-%m"),
                "month_name": month_start.strftime("%b %Y"),
                "dso": dso,
                "ar_balance": ar_at_month_end,
                "monthly_sales": monthly_sales,
                "target": 35
            })

        return trends

    async def get_dso_by_segment(
        self,
        segment_type: str = "salesperson"  # salesperson, customer_type, branch
    ) -> List[Dict]:
        """
        Get DSO broken down by segment.
        """
        today = date.today()
        ninety_days_ago = today - timedelta(days=90)

        if segment_type == "salesperson":
            group_field = Customer.salesperson_id
            label_field = Customer.salesperson_id
        elif segment_type == "customer_type":
            group_field = Customer.customer_type
            label_field = Customer.customer_type
        else:  # branch
            group_field = Customer.branch_id
            label_field = Customer.branch_id

        # Get AR by segment
        ar_result = await self.db.execute(
            select(
                label_field.label('segment'),
                func.sum(Invoice.open_balance).label('ar')
            )
            .join(Invoice, Customer.id == Invoice.customer_id)
            .where(Invoice.open_balance > 0)
            .group_by(group_field)
        )
        ar_by_segment = {row.segment: float(row.ar or 0) for row in ar_result.all()}

        # Get sales by segment (last 90 days)
        sales_result = await self.db.execute(
            select(
                label_field.label('segment'),
                func.sum(Invoice.original_amount).label('sales')
            )
            .join(Invoice, Customer.id == Invoice.customer_id)
            .where(
                Invoice.invoice_date >= ninety_days_ago,
                Invoice.invoice_date <= today
            )
            .group_by(group_field)
        )
        sales_by_segment = {row.segment: float(row.sales or 0) for row in sales_result.all()}

        # Calculate DSO by segment
        segments = []
        for segment_id in set(list(ar_by_segment.keys()) + list(sales_by_segment.keys())):
            ar = ar_by_segment.get(segment_id, 0)
            sales = sales_by_segment.get(segment_id, 0)
            avg_daily = sales / 90 if sales > 0 else 0
            dso = round(ar / avg_daily) if avg_daily > 0 else 0

            segments.append({
                "segment": segment_id or "Unassigned",
                "segment_type": segment_type,
                "ar_balance": ar,
                "90_day_sales": sales,
                "dso": dso,
                "target": 35,
                "variance": dso - 35
            })

        # Sort by DSO descending
        segments.sort(key=lambda x: x['dso'], reverse=True)

        return segments

    async def get_dso_alerts(self) -> List[Dict]:
        """
        Get customers with DSO significantly above average.
        """
        today = date.today()
        ninety_days_ago = today - timedelta(days=90)

        # Calculate company-wide DSO first
        company_dso = await self.calculate_current_dso()
        avg_dso = company_dso['dso']['current']

        # Get customer-level data
        result = await self.db.execute(
            select(
                Customer.id,
                Customer.name,
                func.sum(Invoice.open_balance).label('ar'),
                func.sum(
                    case(
                        (Invoice.invoice_date >= ninety_days_ago, Invoice.original_amount),
                        else_=0
                    )
                ).label('sales_90')
            )
            .join(Invoice, Customer.id == Invoice.customer_id)
            .where(Invoice.open_balance > 0)
            .group_by(Customer.id, Customer.name)
            .having(func.sum(Invoice.open_balance) > 1000)  # Only significant balances
        )

        alerts = []
        for row in result.all():
            ar = float(row.ar or 0)
            sales = float(row.sales_90 or 0)
            avg_daily = sales / 90 if sales > 0 else 0
            customer_dso = round(ar / avg_daily) if avg_daily > 0 else 0

            # Alert if customer DSO is 50% above company average
            if customer_dso > avg_dso * 1.5:
                alerts.append({
                    "customer_id": row.id,
                    "customer_name": row.name,
                    "customer_dso": customer_dso,
                    "company_dso": avg_dso,
                    "variance": customer_dso - avg_dso,
                    "variance_pct": round((customer_dso - avg_dso) / avg_dso * 100) if avg_dso > 0 else 0,
                    "ar_balance": ar,
                    "severity": "high" if customer_dso > avg_dso * 2 else "medium"
                })

        # Sort by variance descending
        alerts.sort(key=lambda x: x['variance'], reverse=True)

        return alerts[:20]  # Top 20 problem accounts
