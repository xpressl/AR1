"""
Dashboard API Routes - Core metrics and summary data
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import date, datetime, timedelta

from src.db.connection import get_db
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.payment import Payment
from src.models.alert import Alert
from src.models.note import Note
from src.models.import_run import ImportRun

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    branch_id: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get main dashboard summary with all key metrics.
    This is the primary endpoint for the dashboard page.
    """
    # Get all open invoices
    inv_query = select(Invoice).where(Invoice.open_balance > 0)
    if branch_id:
        inv_query = inv_query.where(Invoice.branch_id == branch_id)
    if salesperson_id:
        inv_query = inv_query.where(Invoice.salesperson_id == salesperson_id)

    result = await db.execute(inv_query)
    invoices = result.scalars().all()

    # Calculate aging
    aging = {
        "current": {"count": 0, "amount": 0.0},
        "1-30": {"count": 0, "amount": 0.0},
        "31-60": {"count": 0, "amount": 0.0},
        "61-90": {"count": 0, "amount": 0.0},
        "90+": {"count": 0, "amount": 0.0}
    }

    for inv in invoices:
        bucket = inv.aging_bucket
        if bucket in aging:
            aging[bucket]["count"] += 1
            aging[bucket]["amount"] += float(inv.open_balance)

    total_ar = sum(a["amount"] for a in aging.values())
    total_past_due = total_ar - aging["current"]["amount"]

    # Get alert counts
    alert_result = await db.execute(
        select(Alert).where(Alert.is_active == True)
    )
    alerts = alert_result.scalars().all()

    alert_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for a in alerts:
        alert_counts[a.severity] = alert_counts.get(a.severity, 0) + 1

    # Get inactive but owing count
    cust_result = await db.execute(select(Customer).where(Customer.current_balance > 0))
    customers = cust_result.scalars().all()
    inactive_count = sum(1 for c in customers if c.is_inactive)
    inactive_amount = sum(float(c.current_balance or 0) for c in customers if c.is_inactive)

    # Over credit limit
    over_limit_count = sum(1 for c in customers if c.is_over_credit_limit)
    over_limit_amount = sum(float(c.current_balance or 0) for c in customers if c.is_over_credit_limit)

    # Broken promises
    promise_result = await db.execute(
        select(Note)
        .where(Note.note_type == "promise_to_pay")
        .where(Note.promise_status == "broken")
    )
    broken_promises = len(promise_result.scalars().all())

    # Get last import status
    import_result = await db.execute(
        select(ImportRun).order_by(ImportRun.started_at.desc()).limit(1)
    )
    last_import = import_result.scalar_one_or_none()

    # Recent cash (last 7 days)
    week_ago = date.today() - timedelta(days=7)
    cash_result = await db.execute(
        select(func.sum(Payment.amount))
        .where(Payment.payment_date >= week_ago)
    )
    recent_cash = float(cash_result.scalar() or 0)

    return {
        "total_ar": total_ar,
        "total_past_due": total_past_due,
        "past_due_percent": (total_past_due / total_ar * 100) if total_ar > 0 else 0,
        "aging": aging,
        "alerts": {
            "critical": alert_counts["Critical"],
            "high": alert_counts["High"],
            "medium": alert_counts["Medium"],
            "low": alert_counts["Low"],
            "total": sum(alert_counts.values())
        },
        "risk_indicators": {
            "inactive_but_owing": {
                "count": inactive_count,
                "amount": inactive_amount
            },
            "over_credit_limit": {
                "count": over_limit_count,
                "amount": over_limit_amount
            },
            "broken_promises": broken_promises
        },
        "recent_cash_7_days": recent_cash,
        "last_import": {
            "status": last_import.status if last_import else None,
            "timestamp": last_import.started_at.isoformat() if last_import else None
        }
    }


@router.get("/top-overdue")
async def get_top_overdue_customers(
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get top overdue customers by balance"""
    result = await db.execute(select(Customer).where(Customer.current_balance > 0))
    customers = result.scalars().all()

    # Calculate past due amount per customer
    customer_data = []
    for c in customers:
        # Get past due invoices
        inv_result = await db.execute(
            select(Invoice)
            .where(Invoice.customer_id == c.id)
            .where(Invoice.open_balance > 0)
        )
        invoices = inv_result.scalars().all()
        past_due = sum(float(inv.open_balance) for inv in invoices if inv.is_past_due)
        oldest_days = max((inv.days_past_due for inv in invoices), default=0)

        if past_due > 0:
            customer_data.append({
                "id": c.id,
                "name": c.name,
                "total_balance": float(c.current_balance or 0),
                "past_due_amount": past_due,
                "oldest_days_past_due": oldest_days,
                "credit_utilization": c.credit_utilization,
                "is_inactive": c.is_inactive,
                "status": c.status
            })

    # Sort by past due amount
    customer_data.sort(key=lambda x: x["past_due_amount"], reverse=True)

    return customer_data[:limit]


@router.get("/top-over-limit")
async def get_top_over_credit_limit(
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get customers over credit limit"""
    result = await db.execute(
        select(Customer)
        .where(Customer.credit_limit > 0)
        .where(Customer.current_balance > 0)
    )
    customers = result.scalars().all()

    over_limit = [
        {
            "id": c.id,
            "name": c.name,
            "credit_limit": float(c.credit_limit),
            "current_balance": float(c.current_balance or 0),
            "over_by": float((c.current_balance or 0) - c.credit_limit),
            "utilization_percent": c.credit_utilization
        }
        for c in customers if c.is_over_credit_limit
    ]

    over_limit.sort(key=lambda x: x["over_by"], reverse=True)
    return over_limit[:limit]


@router.get("/worklist-preview")
async def get_worklist_preview(
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get prioritized worklist preview for dashboard"""
    # Get customers with balance
    result = await db.execute(
        select(Customer).where(Customer.current_balance > 0)
    )
    customers = result.scalars().all()

    worklist = []
    for c in customers:
        # Calculate priority score
        score = 0

        # Days since last invoice (inactive penalty)
        days_inactive = c.days_since_last_invoice or 0
        if days_inactive > 90:
            score += 25
        if days_inactive > 120:
            score += 25
        if days_inactive > 180:
            score += 25

        # Credit utilization
        if c.is_over_credit_limit:
            score += 30
        elif c.is_near_credit_limit:
            score += 15

        # Get oldest invoice days past due
        inv_result = await db.execute(
            select(Invoice)
            .where(Invoice.customer_id == c.id)
            .where(Invoice.open_balance > 0)
            .order_by(Invoice.due_date.asc())
            .limit(1)
        )
        oldest_inv = inv_result.scalar_one_or_none()
        oldest_days = oldest_inv.days_past_due if oldest_inv else 0

        score += oldest_days * 2

        # Balance factor
        score += float(c.current_balance or 0) / 1000

        # Get active alerts
        alert_result = await db.execute(
            select(Alert)
            .where(Alert.customer_id == c.id)
            .where(Alert.is_active == True)
        )
        alerts = alert_result.scalars().all()
        alert_types = [a.alert_type for a in alerts]
        severities = [a.severity for a in alerts]

        if "Critical" in severities:
            score += 50
        if "broken_promise" in alert_types:
            score += 30

        worklist.append({
            "customer_id": c.id,
            "customer_name": c.name,
            "priority_score": int(score),
            "total_balance": float(c.current_balance or 0),
            "oldest_days_past_due": oldest_days,
            "credit_utilization": c.credit_utilization,
            "is_inactive": c.is_inactive,
            "is_over_limit": c.is_over_credit_limit,
            "alert_types": alert_types,
            "has_critical_alert": "Critical" in severities
        })

    # Sort by priority score
    worklist.sort(key=lambda x: x["priority_score"], reverse=True)

    return worklist[:limit]
