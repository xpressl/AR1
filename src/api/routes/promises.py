"""
Promise Tracking API Routes - Phase 2
Handles promise-to-pay tracking, stats, and broken promise detection.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

from src.db.connection import get_db
from src.models.note import Note
from src.models.customer import Customer

router = APIRouter()


@router.get("/")
async def get_promises(
    status: Optional[str] = None,
    overdue: Optional[bool] = None,
    due_today: Optional[bool] = None,
    customer_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get promise-to-pay notes with filtering.

    Filters:
    - status: pending, kept, broken
    - overdue: true to show only overdue promises
    - due_today: true to show promises due today
    - customer_id: filter by customer
    """
    query = (
        select(Note, Customer.name.label('customer_name'), Customer.billing_phone.label('customer_phone'))
        .join(Customer, Note.customer_id == Customer.id)
        .where(Note.note_type == 'promise_to_pay')
    )

    if status:
        query = query.where(Note.promise_status == status)

    if overdue:
        query = query.where(
            and_(
                Note.promise_status == 'pending',
                Note.promise_date < date.today()
            )
        )

    if due_today:
        query = query.where(
            and_(
                Note.promise_status == 'pending',
                Note.promise_date == date.today()
            )
        )

    if customer_id:
        query = query.where(Note.customer_id == customer_id)

    # Order by: overdue first, then by promise date
    query = query.order_by(
        Note.promise_date.asc()
    ).offset(offset).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    promises = []
    today = date.today()

    for row in rows:
        note = row[0]
        customer_name = row[1]
        customer_phone = row[2]

        promise_date = note.promise_date
        days_until_due = (promise_date - today).days if promise_date else 0
        is_overdue = days_until_due < 0 and note.promise_status == 'pending'

        promises.append({
            "id": note.id,
            "customer_id": note.customer_id,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "promise_amount": float(note.promise_amount) if note.promise_amount else 0,
            "promise_date": promise_date.isoformat() if promise_date else None,
            "status": note.promise_status,
            "content": note.content,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "days_until_due": days_until_due,
            "is_overdue": is_overdue
        })

    return promises


@router.get("/stats")
async def get_promise_stats(db: AsyncSession = Depends(get_db)):
    """Get promise tracking statistics."""
    today = date.today()
    first_of_month = today.replace(day=1)

    # Total pending
    pending_result = await db.execute(
        select(
            func.count(Note.id),
            func.coalesce(func.sum(Note.promise_amount), 0)
        ).where(
            Note.note_type == 'promise_to_pay',
            Note.promise_status == 'pending'
        )
    )
    pending_row = pending_result.one()
    total_pending = pending_row[0]
    total_amount_pending = float(pending_row[1])

    # Due today
    due_today_result = await db.execute(
        select(func.count(Note.id)).where(
            Note.note_type == 'promise_to_pay',
            Note.promise_status == 'pending',
            Note.promise_date == today
        )
    )
    due_today = due_today_result.scalar() or 0

    # Overdue
    overdue_result = await db.execute(
        select(func.count(Note.id)).where(
            Note.note_type == 'promise_to_pay',
            Note.promise_status == 'pending',
            Note.promise_date < today
        )
    )
    overdue = overdue_result.scalar() or 0

    # Kept this month
    kept_result = await db.execute(
        select(func.count(Note.id)).where(
            Note.note_type == 'promise_to_pay',
            Note.promise_status == 'kept',
            Note.promise_date >= first_of_month
        )
    )
    kept_this_month = kept_result.scalar() or 0

    # Broken this month
    broken_result = await db.execute(
        select(func.count(Note.id)).where(
            Note.note_type == 'promise_to_pay',
            Note.promise_status == 'broken',
            Note.promise_date >= first_of_month
        )
    )
    broken_this_month = broken_result.scalar() or 0

    # Calculate kept rate
    total_resolved = kept_this_month + broken_this_month
    kept_rate = round((kept_this_month / total_resolved * 100), 1) if total_resolved > 0 else 100.0

    return {
        "total_pending": total_pending,
        "total_amount_pending": total_amount_pending,
        "due_today": due_today,
        "overdue": overdue,
        "kept_this_month": kept_this_month,
        "broken_this_month": broken_this_month,
        "kept_rate": kept_rate
    }


@router.get("/due-soon")
async def get_promises_due_soon(
    days: int = Query(3, ge=1, le=14),
    db: AsyncSession = Depends(get_db)
):
    """Get promises due within the next N days."""
    today = date.today()
    end_date = today + timedelta(days=days)

    query = (
        select(Note, Customer.name.label('customer_name'))
        .join(Customer, Note.customer_id == Customer.id)
        .where(
            Note.note_type == 'promise_to_pay',
            Note.promise_status == 'pending',
            Note.promise_date >= today,
            Note.promise_date <= end_date
        )
        .order_by(Note.promise_date.asc())
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "id": row[0].id,
            "customer_id": row[0].customer_id,
            "customer_name": row[1],
            "promise_amount": float(row[0].promise_amount) if row[0].promise_amount else 0,
            "promise_date": row[0].promise_date.isoformat() if row[0].promise_date else None,
            "days_until_due": (row[0].promise_date - today).days if row[0].promise_date else 0
        }
        for row in rows
    ]


@router.post("/detect-broken")
async def detect_broken_promises(db: AsyncSession = Depends(get_db)):
    """
    Detect and mark broken promises.
    Run this daily to automatically flag overdue promises as broken.
    Returns count of newly broken promises.
    """
    today = date.today()

    # Find overdue pending promises
    result = await db.execute(
        select(Note).where(
            Note.note_type == 'promise_to_pay',
            Note.promise_status == 'pending',
            Note.promise_date < today
        )
    )
    overdue_promises = result.scalars().all()

    broken_count = 0
    for promise in overdue_promises:
        # Check if payment was received (simplified check)
        # In production, you'd verify against actual payments
        days_overdue = (today - promise.promise_date).days

        # Auto-mark as broken if more than 3 days overdue
        if days_overdue > 3:
            promise.promise_status = 'broken'
            broken_count += 1

            # Create alert for broken promise
            from src.models.alert import Alert
            alert = Alert(
                customer_id=promise.customer_id,
                alert_type='broken_promise',
                severity='Critical',
                title=f'Broken Promise: ${float(promise.promise_amount):,.2f}',
                description=f'Promise to pay ${float(promise.promise_amount):,.2f} by {promise.promise_date} was not kept.',
                requires_action=True
            )
            db.add(alert)

    await db.commit()

    return {
        "detected": len(overdue_promises),
        "auto_marked_broken": broken_count,
        "message": f"Detected {len(overdue_promises)} overdue promises, marked {broken_count} as broken"
    }


@router.get("/performance")
async def get_promise_performance(
    months: int = Query(6, ge=1, le=24),
    db: AsyncSession = Depends(get_db)
):
    """Get promise keeping performance over time."""
    today = date.today()
    start_date = today - timedelta(days=months * 30)

    # Get monthly stats
    query = select(
        func.date_trunc('month', Note.promise_date).label('month'),
        Note.promise_status,
        func.count(Note.id).label('count'),
        func.sum(Note.promise_amount).label('amount')
    ).where(
        Note.note_type == 'promise_to_pay',
        Note.promise_date >= start_date,
        Note.promise_status.in_(['kept', 'broken'])
    ).group_by(
        func.date_trunc('month', Note.promise_date),
        Note.promise_status
    ).order_by(
        func.date_trunc('month', Note.promise_date)
    )

    result = await db.execute(query)
    rows = result.all()

    # Process into monthly data
    monthly_data = {}
    for row in rows:
        month_key = row[0].strftime('%Y-%m') if row[0] else 'unknown'
        if month_key not in monthly_data:
            monthly_data[month_key] = {'kept': 0, 'broken': 0, 'kept_amount': 0, 'broken_amount': 0}

        if row[1] == 'kept':
            monthly_data[month_key]['kept'] = row[2]
            monthly_data[month_key]['kept_amount'] = float(row[3] or 0)
        else:
            monthly_data[month_key]['broken'] = row[2]
            monthly_data[month_key]['broken_amount'] = float(row[3] or 0)

    # Calculate rates
    performance = []
    for month, data in sorted(monthly_data.items()):
        total = data['kept'] + data['broken']
        rate = round(data['kept'] / total * 100, 1) if total > 0 else 0
        performance.append({
            'month': month,
            'kept': data['kept'],
            'broken': data['broken'],
            'kept_rate': rate,
            'kept_amount': data['kept_amount'],
            'broken_amount': data['broken_amount']
        })

    return performance
