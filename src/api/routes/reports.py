"""
Reports API Routes - R01-R05
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import date, timedelta

from src.db.connection import get_db
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.payment import Payment
from src.models.note import Note

router = APIRouter()


@router.get("/aging")
async def get_aging_report(
    branch_id: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Detailed aging report by customer"""
    query = select(Customer).where(Customer.current_balance > 0)

    if branch_id:
        query = query.where(Customer.branch_id == branch_id)
    if salesperson_id:
        query = query.where(Customer.salesperson_id == salesperson_id)

    result = await db.execute(query)
    customers = result.scalars().all()

    report = []
    totals = {"current": 0, "1-30": 0, "31-60": 0, "61-90": 0, "90+": 0, "total": 0}

    for c in customers:
        # Get invoices for this customer
        inv_result = await db.execute(
            select(Invoice)
            .where(Invoice.customer_id == c.id)
            .where(Invoice.open_balance > 0)
        )
        invoices = inv_result.scalars().all()

        aging = {"current": 0, "1-30": 0, "31-60": 0, "61-90": 0, "90+": 0}
        for inv in invoices:
            bucket = inv.aging_bucket
            aging[bucket] = aging.get(bucket, 0) + float(inv.open_balance)

        total = sum(aging.values())

        report.append({
            "customer_id": c.id,
            "customer_name": c.name,
            "salesperson": c.salesperson_name,
            "branch": c.branch_id,
            "current": aging["current"],
            "days_1_30": aging["1-30"],
            "days_31_60": aging["31-60"],
            "days_61_90": aging["61-90"],
            "days_90_plus": aging["90+"],
            "total": total
        })

        for bucket in totals:
            if bucket == "total":
                totals[bucket] += total
            else:
                totals[bucket] += aging.get(bucket, 0)

    return {
        "customers": report,
        "totals": totals,
        "generated_at": date.today().isoformat()
    }


@router.get("/dso")
async def get_dso_report(
    period_days: int = Query(90, ge=30, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Calculate Days Sales Outstanding"""
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)

    # Get total AR
    ar_result = await db.execute(
        select(func.sum(Invoice.open_balance)).where(Invoice.open_balance > 0)
    )
    total_ar = float(ar_result.scalar() or 0)

    # Get credit sales in period (invoices created)
    sales_result = await db.execute(
        select(func.sum(Invoice.original_amount))
        .where(Invoice.invoice_date >= start_date)
        .where(Invoice.invoice_date <= end_date)
    )
    credit_sales = float(sales_result.scalar() or 0)

    # Calculate DSO
    if credit_sales > 0:
        dso = (total_ar / credit_sales) * period_days
    else:
        dso = 0

    # DSO by salesperson
    sp_result = await db.execute(
        select(Customer.salesperson_id, Customer.salesperson_name)
        .where(Customer.current_balance > 0)
        .distinct()
    )
    salespersons = sp_result.all()

    dso_by_salesperson = []
    for sp_id, sp_name in salespersons:
        if not sp_id:
            continue

        sp_ar_result = await db.execute(
            select(func.sum(Invoice.open_balance))
            .join(Customer)
            .where(Invoice.open_balance > 0)
            .where(Customer.salesperson_id == sp_id)
        )
        sp_ar = float(sp_ar_result.scalar() or 0)

        sp_sales_result = await db.execute(
            select(func.sum(Invoice.original_amount))
            .join(Customer)
            .where(Invoice.invoice_date >= start_date)
            .where(Customer.salesperson_id == sp_id)
        )
        sp_sales = float(sp_sales_result.scalar() or 0)

        sp_dso = (sp_ar / sp_sales * period_days) if sp_sales > 0 else 0

        dso_by_salesperson.append({
            "salesperson_id": sp_id,
            "salesperson_name": sp_name,
            "ar_balance": sp_ar,
            "credit_sales": sp_sales,
            "dso": round(sp_dso, 1)
        })

    return {
        "overall_dso": round(dso, 1),
        "total_ar": total_ar,
        "credit_sales": credit_sales,
        "period_days": period_days,
        "by_salesperson": dso_by_salesperson,
        "generated_at": date.today().isoformat()
    }


@router.get("/cash-forecast")
async def get_cash_forecast(
    weeks: int = Query(8, ge=4, le=12),
    db: AsyncSession = Depends(get_db)
):
    """Cash flow forecast based on due dates and promises"""
    today = date.today()
    forecast = []

    for week in range(weeks):
        week_start = today + timedelta(weeks=week)
        week_end = week_start + timedelta(days=6)

        # Get invoices due this week
        inv_result = await db.execute(
            select(Invoice)
            .where(Invoice.open_balance > 0)
            .where(Invoice.due_date >= week_start)
            .where(Invoice.due_date <= week_end)
        )
        invoices = inv_result.scalars().all()
        due_amount = sum(float(inv.open_balance) for inv in invoices)

        # Get promises for this week
        promise_result = await db.execute(
            select(Note)
            .where(Note.note_type == "promise_to_pay")
            .where(Note.promise_status == "pending")
            .where(Note.promise_date >= week_start)
            .where(Note.promise_date <= week_end)
        )
        promises = promise_result.scalars().all()
        promise_amount = sum(float(p.promise_amount or 0) for p in promises)

        # Apply collection probability (historical assumption)
        expected = (due_amount * 0.6) + (promise_amount * 0.8)

        forecast.append({
            "week": week + 1,
            "start_date": week_start.isoformat(),
            "end_date": week_end.isoformat(),
            "invoices_due": due_amount,
            "promises": promise_amount,
            "expected_cash": round(expected, 2)
        })

    return {
        "forecast": forecast,
        "total_expected": sum(f["expected_cash"] for f in forecast),
        "generated_at": date.today().isoformat()
    }


@router.get("/collections-performance")
async def get_collections_performance(
    period_days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db)
):
    """Collections team performance metrics"""
    start_date = date.today() - timedelta(days=period_days)

    # Get notes (calls, emails)
    note_result = await db.execute(
        select(Note)
        .where(Note.created_at >= start_date)
        .where(Note.note_type.in_(["call", "email"]))
    )
    notes = note_result.scalars().all()

    # Get payments
    payment_result = await db.execute(
        select(Payment).where(Payment.payment_date >= start_date)
    )
    payments = payment_result.scalars().all()

    # Get promises
    promise_result = await db.execute(
        select(Note)
        .where(Note.note_type == "promise_to_pay")
        .where(Note.created_at >= start_date)
    )
    promises = promise_result.scalars().all()

    kept = sum(1 for p in promises if p.promise_status == "kept")
    broken = sum(1 for p in promises if p.promise_status == "broken")
    pending = sum(1 for p in promises if p.promise_status == "pending")

    return {
        "period_days": period_days,
        "contacts": {
            "calls": sum(1 for n in notes if n.note_type == "call"),
            "emails": sum(1 for n in notes if n.note_type == "email"),
            "total": len(notes)
        },
        "payments": {
            "count": len(payments),
            "total_amount": sum(float(p.amount) for p in payments)
        },
        "promises": {
            "total": len(promises),
            "kept": kept,
            "broken": broken,
            "pending": pending,
            "success_rate": (kept / (kept + broken) * 100) if (kept + broken) > 0 else 0
        },
        "generated_at": date.today().isoformat()
    }
