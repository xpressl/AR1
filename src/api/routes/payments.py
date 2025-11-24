"""
Payment API Routes - B04
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

from src.db.connection import get_db
from src.models.payment import Payment, PaymentApplication
from src.models.customer import Customer

router = APIRouter()


class PaymentResponse(BaseModel):
    id: int
    epicor_payment_id: str
    customer_id: int
    customer_name: Optional[str] = None
    payment_date: date
    amount: Decimal
    payment_type: Optional[str] = None
    check_number: Optional[str] = None
    reference_number: Optional[str] = None
    unapplied_amount: Decimal
    is_fully_applied: bool

    class Config:
        from_attributes = True


@router.get("/")
async def list_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    customer_id: Optional[int] = None,
    unapplied_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List payments with filtering"""
    query = select(Payment, Customer.name).join(Customer)

    if customer_id:
        query = query.where(Payment.customer_id == customer_id)
    if unapplied_only:
        query = query.where(Payment.unapplied_amount > 0)

    query = query.order_by(Payment.payment_date.desc())

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    return [
        PaymentResponse(
            id=p.id,
            epicor_payment_id=p.epicor_payment_id,
            customer_id=p.customer_id,
            customer_name=cname,
            payment_date=p.payment_date,
            amount=p.amount,
            payment_type=p.payment_type,
            check_number=p.check_number,
            reference_number=p.reference_number,
            unapplied_amount=p.unapplied_amount or 0,
            is_fully_applied=p.is_fully_applied
        )
        for p, cname in rows
    ]


@router.get("/unapplied")
async def get_unapplied_payments(db: AsyncSession = Depends(get_db)):
    """Get all payments with unapplied amounts"""
    result = await db.execute(
        select(Payment, Customer.name)
        .join(Customer)
        .where(Payment.unapplied_amount > 0)
        .order_by(Payment.unapplied_amount.desc())
    )
    rows = result.all()

    total_unapplied = sum(float(p.unapplied_amount or 0) for p, _ in rows)

    return {
        "payments": [
            {
                "id": p.id,
                "customer_id": p.customer_id,
                "customer_name": cname,
                "payment_date": p.payment_date.isoformat(),
                "total_amount": float(p.amount),
                "unapplied_amount": float(p.unapplied_amount or 0)
            }
            for p, cname in rows
        ],
        "total_unapplied": total_unapplied,
        "count": len(rows)
    }


@router.get("/summary")
async def get_payments_summary(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get payment summary for recent period"""
    from datetime import datetime, timedelta
    cutoff = datetime.now().date() - timedelta(days=days)

    result = await db.execute(
        select(Payment).where(Payment.payment_date >= cutoff)
    )
    payments = result.scalars().all()

    by_type = {}
    for p in payments:
        ptype = p.payment_type or "Unknown"
        if ptype not in by_type:
            by_type[ptype] = {"count": 0, "amount": 0}
        by_type[ptype]["count"] += 1
        by_type[ptype]["amount"] += float(p.amount)

    return {
        "period_days": days,
        "total_payments": len(payments),
        "total_amount": sum(float(p.amount) for p in payments),
        "by_type": by_type
    }
