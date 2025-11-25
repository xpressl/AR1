"""
Report Service

Generates advanced reports and analytics for AR Control Hub
"""
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case, desc
from sqlalchemy.orm import joinedload

from src.models import Customer, Invoice, Payment, User, Note, Task, Dispute


class ReportService:
    """Service for generating advanced reports and analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_executive_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Generate executive AR summary report.

        High-level KPIs for leadership.
        """
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=90)

        # Total AR
        total_ar_query = select(
            func.coalesce(func.sum(Invoice.open_balance), 0).label('total_ar')
        ).where(Invoice.status == 'Open')

        total_ar_result = await self.db.execute(total_ar_query)
        total_ar = float(total_ar_result.scalar() or 0)

        # Aging breakdown
        today = date.today()
        aging_query = select(
            func.sum(
                case((Invoice.days_overdue <= 30, Invoice.open_balance), else_=0)
            ).label('current_30'),
            func.sum(
                case((and_(Invoice.days_overdue > 30, Invoice.days_overdue <= 60), Invoice.open_balance), else_=0)
            ).label('days_31_60'),
            func.sum(
                case((and_(Invoice.days_overdue > 60, Invoice.days_overdue <= 90), Invoice.open_balance), else_=0)
            ).label('days_61_90'),
            func.sum(
                case((Invoice.days_overdue > 90, Invoice.open_balance), else_=0)
            ).label('days_over_90')
        ).where(Invoice.status == 'Open')

        aging_result = await self.db.execute(aging_query)
        aging_row = aging_result.first()

        aging_breakdown = {
            'current_30': float(aging_row.current_30 or 0),
            'days_31_60': float(aging_row.days_31_60 or 0),
            'days_61_90': float(aging_row.days_61_90 or 0),
            'days_over_90': float(aging_row.days_over_90 or 0)
        }

        # DSO Calculation (simplified - 30-day rolling)
        days_sales = 30
        sales_query = select(
            func.sum(Invoice.total_amount)
        ).where(
            and_(
                Invoice.invoice_date >= end_date - timedelta(days=days_sales),
                Invoice.invoice_date <= end_date
            )
        )

        sales_result = await self.db.execute(sales_query)
        sales = float(sales_result.scalar() or 1)  # Avoid division by zero

        dso = (total_ar / sales) * days_sales if sales > 0 else 0

        # Collection Effectiveness Index (CEI)
        # CEI = (Beginning AR + Period Sales - Ending AR) / (Beginning AR + Period Sales - Ending Current AR) * 100

        beginning_ar_query = select(
            func.coalesce(func.sum(Invoice.open_balance), 0)
        ).where(
            and_(
                Invoice.status == 'Open',
                Invoice.invoice_date < start_date
            )
        )
        beginning_ar_result = await self.db.execute(beginning_ar_query)
        beginning_ar = float(beginning_ar_result.scalar() or 0)

        period_sales = sales
        ending_ar = total_ar
        ending_current_ar = aging_breakdown['current_30']

        numerator = beginning_ar + period_sales - ending_ar
        denominator = beginning_ar + period_sales - ending_current_ar
        cei = (numerator / denominator * 100) if denominator > 0 else 0

        # Top 10 customers by balance
        top_customers_query = select(
            Customer.id,
            Customer.name,
            func.sum(Invoice.open_balance).label('total_balance')
        ).join(
            Invoice, Invoice.customer_id == Customer.id
        ).where(
            Invoice.status == 'Open'
        ).group_by(
            Customer.id, Customer.name
        ).order_by(
            desc('total_balance')
        ).limit(10)

        top_customers_result = await self.db.execute(top_customers_query)
        top_customers = [
            {
                'customer_id': str(row.id),
                'customer_name': row.name,
                'balance': float(row.total_balance)
            }
            for row in top_customers_result.fetchall()
        ]

        # Active disputes count
        disputes_query = select(func.count(Dispute.id)).where(
            Dispute.status.in_(['Open', 'In Review'])
        )
        disputes_result = await self.db.execute(disputes_query)
        active_disputes = disputes_result.scalar() or 0

        # Past due percentage
        past_due = aging_breakdown['days_31_60'] + aging_breakdown['days_61_90'] + aging_breakdown['days_over_90']
        past_due_percentage = (past_due / total_ar * 100) if total_ar > 0 else 0

        return {
            'summary': {
                'total_ar': total_ar,
                'dso': round(dso, 1),
                'cei': round(cei, 1),
                'past_due_percentage': round(past_due_percentage, 1),
                'active_disputes': active_disputes,
                'active_customers': await self._get_active_customer_count()
            },
            'aging_breakdown': aging_breakdown,
            'top_customers': top_customers,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'generated_at': datetime.utcnow().isoformat()
        }

    async def get_collection_performance(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate collection performance report.

        Tracks collections by team member, promises, contact frequency.
        """
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Collections by user (from payments)
        collections_query = select(
            Payment.received_by,
            User.full_name,
            func.count(Payment.id).label('payment_count'),
            func.sum(Payment.amount).label('total_collected')
        ).join(
            User, User.id == Payment.received_by, isouter=True
        ).where(
            and_(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            )
        )

        if user_id:
            collections_query = collections_query.where(Payment.received_by == user_id)

        collections_query = collections_query.group_by(
            Payment.received_by, User.full_name
        ).order_by(
            desc('total_collected')
        )

        collections_result = await self.db.execute(collections_query)
        collections_by_user = [
            {
                'user_id': str(row.received_by) if row.received_by else None,
                'user_name': row.full_name or 'Unassigned',
                'payment_count': row.payment_count,
                'total_collected': float(row.total_collected or 0)
            }
            for row in collections_result.fetchall()
        ]

        # Contact activity (notes and tasks)
        activity_query = select(
            Note.created_by,
            User.full_name,
            func.count(Note.id).label('contact_count')
        ).join(
            User, User.id == Note.created_by, isouter=True
        ).where(
            and_(
                Note.created_at >= start_date,
                Note.created_at <= end_date,
                Note.note_type.in_(['call', 'email'])
            )
        )

        if user_id:
            activity_query = activity_query.where(Note.created_by == user_id)

        activity_query = activity_query.group_by(
            Note.created_by, User.full_name
        ).order_by(
            desc('contact_count')
        )

        activity_result = await self.db.execute(activity_query)
        activity_by_user = [
            {
                'user_id': str(row.created_by) if row.created_by else None,
                'user_name': row.full_name or 'Unknown',
                'contact_count': row.contact_count
            }
            for row in activity_result.fetchall()
        ]

        # Promises made vs kept (from tasks)
        # This is simplified - in reality you'd track promise_to_pay table
        promises_query = select(
            Task.assigned_to,
            User.full_name,
            func.count(Task.id).label('promises_made'),
            func.count(case((Task.status == 'completed', Task.id))).label('promises_kept')
        ).join(
            User, User.id == Task.assigned_to, isouter=True
        ).where(
            and_(
                Task.created_at >= start_date,
                Task.created_at <= end_date,
                Task.task_type == 'follow_up'
            )
        )

        if user_id:
            promises_query = promises_query.where(Task.assigned_to == user_id)

        promises_query = promises_query.group_by(
            Task.assigned_to, User.full_name
        )

        promises_result = await self.db.execute(promises_query)
        promises_by_user = [
            {
                'user_id': str(row.assigned_to) if row.assigned_to else None,
                'user_name': row.full_name or 'Unassigned',
                'promises_made': row.promises_made,
                'promises_kept': row.promises_kept,
                'promise_kept_rate': (row.promises_kept / row.promises_made * 100) if row.promises_made > 0 else 0
            }
            for row in promises_result.fetchall()
        ]

        # Overall collection rate
        beginning_ar = await self._get_ar_balance_at_date(start_date)
        ending_ar = await self._get_ar_balance_at_date(end_date)
        total_collected = sum(u['total_collected'] for u in collections_by_user)

        collection_rate = (total_collected / beginning_ar * 100) if beginning_ar > 0 else 0

        return {
            'collections_by_user': collections_by_user,
            'activity_by_user': activity_by_user,
            'promises_by_user': promises_by_user,
            'summary': {
                'total_collected': total_collected,
                'beginning_ar': beginning_ar,
                'ending_ar': ending_ar,
                'collection_rate': round(collection_rate, 1)
            },
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'generated_at': datetime.utcnow().isoformat()
        }

    async def get_customer_segmentation(self) -> Dict[str, Any]:
        """
        Generate customer segmentation report.

        Segments customers by risk, payment behavior, credit utilization.
        """
        # Risk tier distribution (simplified - would use actual risk scoring)
        customers_query = select(
            Customer.id,
            Customer.name,
            Customer.credit_limit,
            func.coalesce(func.sum(Invoice.open_balance), 0).label('balance'),
            func.count(Invoice.id).label('invoice_count'),
            func.count(
                case((Invoice.days_overdue > 30, Invoice.id))
            ).label('overdue_invoices')
        ).outerjoin(
            Invoice, and_(Invoice.customer_id == Customer.id, Invoice.status == 'Open')
        ).group_by(
            Customer.id, Customer.name, Customer.credit_limit
        )

        result = await self.db.execute(customers_query)
        customers = result.fetchall()

        # Segment customers into risk tiers
        low_risk = []
        medium_risk = []
        high_risk = []
        critical_risk = []

        for customer in customers:
            balance = float(customer.balance)
            credit_limit = float(customer.credit_limit or 0)
            credit_utilization = (balance / credit_limit * 100) if credit_limit > 0 else 0

            customer_data = {
                'customer_id': str(customer.id),
                'customer_name': customer.name,
                'balance': balance,
                'credit_limit': credit_limit,
                'credit_utilization': round(credit_utilization, 1),
                'invoice_count': customer.invoice_count,
                'overdue_invoices': customer.overdue_invoices
            }

            # Simple risk scoring (can be enhanced with actual risk algorithm)
            if customer.overdue_invoices > 5 or credit_utilization > 90:
                critical_risk.append(customer_data)
            elif customer.overdue_invoices > 2 or credit_utilization > 75:
                high_risk.append(customer_data)
            elif customer.overdue_invoices > 0 or credit_utilization > 50:
                medium_risk.append(customer_data)
            else:
                low_risk.append(customer_data)

        return {
            'segmentation': {
                'low_risk': {
                    'count': len(low_risk),
                    'customers': low_risk[:10]  # Top 10 only
                },
                'medium_risk': {
                    'count': len(medium_risk),
                    'customers': medium_risk[:10]
                },
                'high_risk': {
                    'count': len(high_risk),
                    'customers': high_risk[:10]
                },
                'critical_risk': {
                    'count': len(critical_risk),
                    'customers': critical_risk
                }
            },
            'summary': {
                'total_customers': len(customers),
                'low_risk_count': len(low_risk),
                'medium_risk_count': len(medium_risk),
                'high_risk_count': len(high_risk),
                'critical_risk_count': len(critical_risk)
            },
            'generated_at': datetime.utcnow().isoformat()
        }

    async def get_aging_detail(
        self,
        customer_id: Optional[str] = None,
        min_balance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate detailed aging report with invoice-level detail.
        """
        query = select(
            Customer.id.label('customer_id'),
            Customer.name.label('customer_name'),
            Invoice.id.label('invoice_id'),
            Invoice.invoice_number,
            Invoice.invoice_date,
            Invoice.due_date,
            Invoice.total_amount,
            Invoice.open_balance,
            Invoice.days_overdue,
            case(
                (Invoice.days_overdue <= 30, '0-30'),
                (Invoice.days_overdue <= 60, '31-60'),
                (Invoice.days_overdue <= 90, '61-90'),
                else_='90+'
            ).label('aging_bucket')
        ).join(
            Customer, Invoice.customer_id == Customer.id
        ).where(
            Invoice.status == 'Open'
        )

        if customer_id:
            query = query.where(Customer.id == customer_id)

        if min_balance:
            query = query.where(Invoice.open_balance >= min_balance)

        query = query.order_by(desc(Invoice.open_balance))

        result = await self.db.execute(query)
        invoices = [
            {
                'customer_id': str(row.customer_id),
                'customer_name': row.customer_name,
                'invoice_id': str(row.invoice_id),
                'invoice_number': row.invoice_number,
                'invoice_date': row.invoice_date.isoformat() if row.invoice_date else None,
                'due_date': row.due_date.isoformat() if row.due_date else None,
                'total_amount': float(row.total_amount),
                'open_balance': float(row.open_balance),
                'days_overdue': row.days_overdue,
                'aging_bucket': row.aging_bucket
            }
            for row in result.fetchall()
        ]

        # Summary by aging bucket
        summary = {
            '0-30': sum(inv['open_balance'] for inv in invoices if inv['aging_bucket'] == '0-30'),
            '31-60': sum(inv['open_balance'] for inv in invoices if inv['aging_bucket'] == '31-60'),
            '61-90': sum(inv['open_balance'] for inv in invoices if inv['aging_bucket'] == '61-90'),
            '90+': sum(inv['open_balance'] for inv in invoices if inv['aging_bucket'] == '90+')
        }

        return {
            'invoices': invoices,
            'summary': summary,
            'total_ar': sum(summary.values()),
            'invoice_count': len(invoices),
            'generated_at': datetime.utcnow().isoformat()
        }

    # Helper methods

    async def _get_active_customer_count(self) -> int:
        """Get count of active customers."""
        query = select(func.count(Customer.id)).where(Customer.status == 'Active')
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def _get_ar_balance_at_date(self, target_date: date) -> float:
        """Get AR balance at a specific date."""
        query = select(
            func.coalesce(func.sum(Invoice.open_balance), 0)
        ).where(
            and_(
                Invoice.status == 'Open',
                Invoice.invoice_date <= target_date
            )
        )
        result = await self.db.execute(query)
        return float(result.scalar() or 0)
