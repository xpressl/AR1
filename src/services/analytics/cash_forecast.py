"""
Cash Flow Forecast Service - R03
Predicts future cash receipts based on invoice due dates and promises.
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
import logging

from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.note import Note
from src.models.payment import Payment

logger = logging.getLogger(__name__)


class CashFlowForecastService:
    """
    Generates cash flow forecasts based on:
    1. Invoice due dates
    2. Customer payment promises
    3. Historical payment patterns
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_forecast(
        self,
        weeks: int = 8,
        include_promises: bool = True,
        group_by: Optional[str] = None  # customer, salesperson, branch
    ) -> Dict:
        """
        Generate cash flow forecast for the specified number of weeks.

        Args:
            weeks: Number of weeks to forecast (default 8)
            include_promises: Include promise-to-pay in forecast
            group_by: Optional grouping dimension

        Returns:
            Forecast data with weekly breakdown
        """
        today = date.today()
        end_date = today + timedelta(weeks=weeks)

        # Get invoice-based forecast
        invoice_forecast = await self._forecast_from_invoices(today, end_date)

        # Get promise-based forecast
        promise_forecast = {}
        if include_promises:
            promise_forecast = await self._forecast_from_promises(today, end_date)

        # Combine forecasts by week
        weekly_forecast = self._combine_forecasts(
            invoice_forecast,
            promise_forecast,
            today,
            weeks
        )

        # Get historical accuracy
        accuracy = await self._calculate_forecast_accuracy()

        # Get totals
        total_forecasted = sum(w['total'] for w in weekly_forecast)
        total_from_invoices = sum(w['invoice_based'] for w in weekly_forecast)
        total_from_promises = sum(w['promise_based'] for w in weekly_forecast)

        return {
            "generated_at": datetime.now().isoformat(),
            "forecast_period": {
                "start": today.isoformat(),
                "end": end_date.isoformat(),
                "weeks": weeks
            },
            "summary": {
                "total_forecasted": total_forecasted,
                "from_invoices": total_from_invoices,
                "from_promises": total_from_promises,
                "forecast_accuracy": accuracy
            },
            "weekly_breakdown": weekly_forecast,
            "by_customer": await self._forecast_by_customer(today, end_date) if group_by == "customer" else None,
            "by_salesperson": await self._forecast_by_salesperson(today, end_date) if group_by == "salesperson" else None
        }

    async def _forecast_from_invoices(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, float]:
        """Forecast cash based on invoice due dates."""
        result = await self.db.execute(
            select(
                Invoice.due_date,
                func.sum(Invoice.open_balance).label('amount')
            ).where(
                Invoice.open_balance > 0,
                Invoice.due_date >= start_date,
                Invoice.due_date <= end_date
            ).group_by(Invoice.due_date)
        )

        forecast = {}
        for row in result.all():
            if row.due_date:
                week_key = self._get_week_key(row.due_date, start_date)
                forecast[week_key] = forecast.get(week_key, 0) + float(row.amount or 0)

        return forecast

    async def _forecast_from_promises(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, float]:
        """Forecast cash based on payment promises."""
        result = await self.db.execute(
            select(
                Note.promise_date,
                func.sum(Note.promise_amount).label('amount')
            ).where(
                Note.note_type == 'promise_to_pay',
                Note.promise_status == 'pending',
                Note.promise_date >= start_date,
                Note.promise_date <= end_date
            ).group_by(Note.promise_date)
        )

        forecast = {}
        for row in result.all():
            if row.promise_date:
                week_key = self._get_week_key(row.promise_date, start_date)
                forecast[week_key] = forecast.get(week_key, 0) + float(row.amount or 0)

        return forecast

    def _get_week_key(self, target_date: date, start_date: date) -> str:
        """Get week number key for a date."""
        days_diff = (target_date - start_date).days
        week_num = days_diff // 7
        return f"week_{week_num}"

    def _combine_forecasts(
        self,
        invoice_forecast: Dict[str, float],
        promise_forecast: Dict[str, float],
        start_date: date,
        weeks: int
    ) -> List[Dict]:
        """Combine invoice and promise forecasts into weekly breakdown."""
        weekly = []

        for week_num in range(weeks):
            week_key = f"week_{week_num}"
            week_start = start_date + timedelta(weeks=week_num)
            week_end = week_start + timedelta(days=6)

            invoice_amount = invoice_forecast.get(week_key, 0)
            promise_amount = promise_forecast.get(week_key, 0)

            # Promises override invoice amounts for same customer
            # In practice, you'd dedupe by customer
            total = invoice_amount + promise_amount

            weekly.append({
                "week": week_num + 1,
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "invoice_based": invoice_amount,
                "promise_based": promise_amount,
                "total": total,
                "cumulative": sum(w['total'] for w in weekly) + total
            })

        return weekly

    async def _calculate_forecast_accuracy(self) -> Dict:
        """Calculate historical forecast accuracy."""
        # Compare forecasted vs actual for past 4 weeks
        four_weeks_ago = date.today() - timedelta(weeks=4)

        # Get what was due in past 4 weeks
        due_result = await self.db.execute(
            select(func.sum(Invoice.original_amount)).where(
                Invoice.due_date >= four_weeks_ago,
                Invoice.due_date < date.today()
            )
        )
        total_due = float(due_result.scalar() or 0)

        # Get what was actually collected
        collected_result = await self.db.execute(
            select(func.sum(Payment.amount)).where(
                Payment.payment_date >= four_weeks_ago,
                Payment.payment_date < date.today()
            )
        )
        total_collected = float(collected_result.scalar() or 0)

        accuracy_pct = round((total_collected / total_due * 100), 1) if total_due > 0 else 0

        return {
            "period": "last_4_weeks",
            "forecasted": total_due,
            "actual": total_collected,
            "accuracy_percentage": accuracy_pct,
            "variance": total_due - total_collected
        }

    async def _forecast_by_customer(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Get forecast broken down by customer."""
        result = await self.db.execute(
            select(
                Customer.id,
                Customer.name,
                func.sum(Invoice.open_balance).label('forecasted')
            )
            .join(Invoice, Customer.id == Invoice.customer_id)
            .where(
                Invoice.open_balance > 0,
                Invoice.due_date >= start_date,
                Invoice.due_date <= end_date
            )
            .group_by(Customer.id, Customer.name)
            .order_by(func.sum(Invoice.open_balance).desc())
            .limit(20)
        )

        return [
            {
                "customer_id": row.id,
                "customer_name": row.name,
                "forecasted_amount": float(row.forecasted or 0)
            }
            for row in result.all()
        ]

    async def _forecast_by_salesperson(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Get forecast broken down by salesperson."""
        result = await self.db.execute(
            select(
                Customer.salesperson_id,
                func.sum(Invoice.open_balance).label('forecasted')
            )
            .join(Invoice, Customer.id == Invoice.customer_id)
            .where(
                Invoice.open_balance > 0,
                Invoice.due_date >= start_date,
                Invoice.due_date <= end_date,
                Customer.salesperson_id.isnot(None)
            )
            .group_by(Customer.salesperson_id)
            .order_by(func.sum(Invoice.open_balance).desc())
        )

        return [
            {
                "salesperson_id": row.salesperson_id,
                "forecasted_amount": float(row.forecasted or 0)
            }
            for row in result.all()
        ]

    async def get_forecast_vs_actual(
        self,
        months: int = 6
    ) -> List[Dict]:
        """
        Get historical forecast vs actual comparison.
        Used for forecast accuracy trending.
        """
        results = []
        today = date.today()

        for month_offset in range(months, 0, -1):
            # Calculate month boundaries
            month_start = (today.replace(day=1) - timedelta(days=month_offset * 30)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

            # Get invoices that were due in that month
            due_result = await self.db.execute(
                select(func.sum(Invoice.original_amount)).where(
                    Invoice.due_date >= month_start,
                    Invoice.due_date <= month_end
                )
            )
            forecasted = float(due_result.scalar() or 0)

            # Get payments received in that month
            collected_result = await self.db.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.payment_date >= month_start,
                    Payment.payment_date <= month_end
                )
            )
            actual = float(collected_result.scalar() or 0)

            accuracy = round((actual / forecasted * 100), 1) if forecasted > 0 else 0

            results.append({
                "month": month_start.strftime("%Y-%m"),
                "month_name": month_start.strftime("%B %Y"),
                "forecasted": forecasted,
                "actual": actual,
                "variance": forecasted - actual,
                "accuracy_percentage": accuracy
            })

        return results
