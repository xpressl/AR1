"""
Salesperson Portal API Routes - Phase 2
Read-only access to AR data for assigned customers.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from typing import Optional
from datetime import date

from src.db.connection import get_db
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.alert import Alert

router = APIRouter()


@router.get("/customers")
async def get_salesperson_customers(
    salesperson_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get customers assigned to a salesperson with AR summary.
    If salesperson_id not provided, returns all customers (for demo).
    """
    # Base customer query
    query = select(Customer)

    if salesperson_id:
        query = query.where(Customer.salesperson_id == salesperson_id)

    query = query.where(Customer.status == 'Active')
    query = query.order_by(Customer.name)

    result = await db.execute(query)
    customers = result.scalars().all()

    customer_summaries = []
    today = date.today()

    for customer in customers:
        # Get invoice stats
        inv_result = await db.execute(
            select(
                func.sum(Invoice.open_balance).label('total_balance'),
                func.sum(
                    case(
                        (Invoice.due_date < today, Invoice.open_balance),
                        else_=0
                    )
                ).label('past_due'),
                func.max(
                    case(
                        (Invoice.open_balance > 0,
                         func.extract('day', func.current_date() - Invoice.invoice_date)),
                        else_=0
                    )
                ).label('oldest_days')
            ).where(
                Invoice.customer_id == customer.id,
                Invoice.open_balance > 0
            )
        )
        inv_stats = inv_result.one()

        # Get alert counts
        alert_result = await db.execute(
            select(
                func.count(Alert.id).label('total'),
                func.sum(case((Alert.severity == 'Critical', 1), else_=0)).label('critical')
            ).where(
                Alert.customer_id == customer.id,
                Alert.status == 'active'
            )
        )
        alert_stats = alert_result.one()

        current_balance = float(inv_stats.total_balance or 0)
        credit_limit = float(customer.credit_limit or 0)
        credit_utilization = round((current_balance / credit_limit * 100), 1) if credit_limit > 0 else 0

        customer_summaries.append({
            "id": customer.id,
            "epicor_customer_id": customer.epicor_customer_id,
            "name": customer.name,
            "current_balance": current_balance,
            "credit_limit": credit_limit,
            "credit_utilization": credit_utilization,
            "past_due_amount": float(inv_stats.past_due or 0),
            "oldest_invoice_days": int(inv_stats.oldest_days or 0),
            "alert_count": int(alert_stats.total or 0),
            "has_critical_alert": (alert_stats.critical or 0) > 0,
            "status": customer.status,
            "last_contact_date": None  # Would come from notes
        })

    # Sort by past due amount descending
    customer_summaries.sort(key=lambda x: x['past_due_amount'], reverse=True)

    return customer_summaries


@router.get("/stats")
async def get_salesperson_stats(
    salesperson_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated stats for salesperson's accounts."""
    today = date.today()

    # Build customer filter
    customer_filter = Customer.status == 'Active'
    if salesperson_id:
        customer_filter = and_(customer_filter, Customer.salesperson_id == salesperson_id)

    # Get customer IDs
    customer_ids_result = await db.execute(
        select(Customer.id).where(customer_filter)
    )
    customer_ids = [row[0] for row in customer_ids_result.all()]

    if not customer_ids:
        return {
            "total_customers": 0,
            "total_ar_balance": 0,
            "total_past_due": 0,
            "critical_alerts": 0,
            "accounts_over_limit": 0,
            "average_days_to_pay": 0
        }

    # Total customers
    total_customers = len(customer_ids)

    # AR totals
    ar_result = await db.execute(
        select(
            func.sum(Invoice.open_balance).label('total_balance'),
            func.sum(
                case(
                    (Invoice.due_date < today, Invoice.open_balance),
                    else_=0
                )
            ).label('past_due')
        ).where(
            Invoice.customer_id.in_(customer_ids),
            Invoice.open_balance > 0
        )
    )
    ar_stats = ar_result.one()

    # Critical alerts
    alert_result = await db.execute(
        select(func.count(Alert.id)).where(
            Alert.customer_id.in_(customer_ids),
            Alert.severity == 'Critical',
            Alert.status == 'active'
        )
    )
    critical_alerts = alert_result.scalar() or 0

    # Accounts over limit
    over_limit_result = await db.execute(
        select(func.count(Customer.id)).where(
            Customer.id.in_(customer_ids),
            Customer.current_balance > Customer.credit_limit
        )
    )
    accounts_over_limit = over_limit_result.scalar() or 0

    # Average days to pay (simplified - would calculate from payment history)
    average_days_to_pay = 32  # Placeholder

    return {
        "total_customers": total_customers,
        "total_ar_balance": float(ar_stats.total_balance or 0),
        "total_past_due": float(ar_stats.past_due or 0),
        "critical_alerts": critical_alerts,
        "accounts_over_limit": accounts_over_limit,
        "average_days_to_pay": average_days_to_pay
    }


@router.get("/customer/{customer_id}")
async def get_customer_detail_readonly(
    customer_id: int,
    salesperson_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get read-only customer detail for salesperson portal.
    Validates that customer is assigned to the salesperson.
    """
    query = select(Customer).where(Customer.id == customer_id)

    if salesperson_id:
        query = query.where(Customer.salesperson_id == salesperson_id)

    result = await db.execute(query)
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found or not assigned to you"
        )

    # Get invoices
    inv_result = await db.execute(
        select(Invoice)
        .where(Invoice.customer_id == customer_id, Invoice.open_balance > 0)
        .order_by(Invoice.due_date.asc())
    )
    invoices = inv_result.scalars().all()

    # Get active alerts
    alert_result = await db.execute(
        select(Alert)
        .where(Alert.customer_id == customer_id, Alert.status == 'active')
        .order_by(Alert.severity.desc())
    )
    alerts = alert_result.scalars().all()

    return {
        "customer": {
            "id": customer.id,
            "epicor_customer_id": customer.epicor_customer_id,
            "name": customer.name,
            "billing_email": customer.billing_email,
            "billing_phone": customer.billing_phone,
            "current_balance": float(customer.current_balance or 0),
            "credit_limit": float(customer.credit_limit or 0),
            "status": customer.status
        },
        "invoices": [
            {
                "id": inv.id,
                "invoice_number": inv.epicor_invoice_number,
                "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
                "original_amount": float(inv.original_amount),
                "open_balance": float(inv.open_balance),
                "days_past_due": inv.days_past_due
            }
            for inv in invoices
        ],
        "alerts": [
            {
                "id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "description": alert.description
            }
            for alert in alerts
        ]
    }
