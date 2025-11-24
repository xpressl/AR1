"""
Salesperson Portal API Routes - Phase 2
Read-only access to AR data for assigned customers.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from typing import Optional, List, Dict
from datetime import date

from src.db.connection import get_db
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.alert import Alert

router = APIRouter()


async def get_current_salesperson_id(
    x_salesperson_id: Optional[str] = Header(None, alias="X-Salesperson-ID"),
    salesperson_id: Optional[str] = Query(None)
) -> Optional[str]:
    """
    Get current salesperson ID from header or query param.
    In production, this would be extracted from JWT token.
    """
    return x_salesperson_id or salesperson_id


@router.get("/customers")
async def get_salesperson_customers(
    current_salesperson: Optional[str] = Depends(get_current_salesperson_id),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get customers assigned to the authenticated salesperson.
    Requires salesperson authentication via header or query param.

    Optimized to use a single query with LEFT JOINs to avoid N+1 problem.
    """
    # Security: Require salesperson_id for non-admin access
    # In production, verify against JWT claims
    if not current_salesperson:
        raise HTTPException(
            status_code=401,
            detail="Salesperson authentication required. Provide X-Salesperson-ID header."
        )

    today = date.today()

    # Optimized: Single query with LEFT JOINs and aggregations
    # This replaces N queries (one per customer) with just one query
    query = select(
        Customer.id,
        Customer.epicor_customer_id,
        Customer.name,
        Customer.credit_limit,
        Customer.status,
        func.coalesce(func.sum(Invoice.open_balance), 0).label('total_balance'),
        func.coalesce(
            func.sum(
                case(
                    (Invoice.due_date < today, Invoice.open_balance),
                    else_=0
                )
            ), 0
        ).label('past_due'),
        func.coalesce(
            func.max(
                case(
                    (Invoice.open_balance > 0,
                     func.extract('day', func.current_date() - Invoice.invoice_date)),
                    else_=0
                )
            ), 0
        ).label('oldest_days'),
        func.count(Alert.id).label('alert_count'),
        func.coalesce(
            func.sum(case((Alert.severity == 'Critical', 1), else_=0)), 0
        ).label('critical_alerts')
    ).select_from(Customer).outerjoin(
        Invoice,
        and_(
            Invoice.customer_id == Customer.id,
            Invoice.open_balance > 0
        )
    ).outerjoin(
        Alert,
        and_(
            Alert.customer_id == Customer.id,
            Alert.status == 'active'
        )
    ).where(
        Customer.salesperson_id == current_salesperson,
        Customer.status == 'Active'
    ).group_by(
        Customer.id,
        Customer.epicor_customer_id,
        Customer.name,
        Customer.credit_limit,
        Customer.status
    ).order_by(Customer.name)

    result = await db.execute(query)
    rows = result.all()

    customer_summaries = []
    for row in rows:
        current_balance = float(row.total_balance)
        credit_limit = float(row.credit_limit or 0)
        credit_utilization = round((current_balance / credit_limit * 100), 1) if credit_limit > 0 else 0

        customer_summaries.append({
            "id": row.id,
            "epicor_customer_id": row.epicor_customer_id,
            "name": row.name,
            "current_balance": current_balance,
            "credit_limit": credit_limit,
            "credit_utilization": credit_utilization,
            "past_due_amount": float(row.past_due),
            "oldest_invoice_days": int(row.oldest_days),
            "alert_count": int(row.alert_count),
            "has_critical_alert": int(row.critical_alerts) > 0,
            "status": row.status,
            "last_contact_date": None  # Would come from notes
        })

    # Sort by past due amount descending
    customer_summaries.sort(key=lambda x: x['past_due_amount'], reverse=True)

    return customer_summaries


@router.get("/stats")
async def get_salesperson_stats(
    current_salesperson: Optional[str] = Depends(get_current_salesperson_id),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Get aggregated stats for salesperson's accounts."""
    if not current_salesperson:
        raise HTTPException(
            status_code=401,
            detail="Salesperson authentication required. Provide X-Salesperson-ID header."
        )

    today = date.today()

    # Filter by authenticated salesperson only
    customer_filter = and_(
        Customer.status == 'Active',
        Customer.salesperson_id == current_salesperson
    )

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
    current_salesperson: Optional[str] = Depends(get_current_salesperson_id),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get read-only customer detail for salesperson portal.
    Validates that customer is assigned to the authenticated salesperson.
    """
    if not current_salesperson:
        raise HTTPException(
            status_code=401,
            detail="Salesperson authentication required. Provide X-Salesperson-ID header."
        )

    # Only allow access to customers assigned to this salesperson
    query = select(Customer).where(
        Customer.id == customer_id,
        Customer.salesperson_id == current_salesperson
    )

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
