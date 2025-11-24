"""
Analytics API Routes - Phase 3
Cash flow forecasting, DSO analysis, and performance metrics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict
from datetime import date

from src.db.connection import get_db
from src.services.analytics.cash_forecast import CashFlowForecastService
from src.services.analytics.dso_analysis import DSOAnalysisService

router = APIRouter()


# Cash Flow Forecast Endpoints

@router.get("/forecast/cash")
async def get_cash_flow_forecast(
    weeks: int = Query(8, ge=1, le=52),
    include_promises: bool = Query(True),
    group_by: Optional[str] = Query(None, regex="^(customer|salesperson|branch)$"),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Generate cash flow forecast for specified weeks.

    Args:
        weeks: Number of weeks to forecast (1-52)
        include_promises: Include promise-to-pay data
        group_by: Optional grouping (customer, salesperson, branch)

    Returns:
        Weekly forecast breakdown with accuracy metrics
    """
    service = CashFlowForecastService(db)
    return await service.generate_forecast(
        weeks=weeks,
        include_promises=include_promises,
        group_by=group_by
    )


@router.get("/forecast/accuracy")
async def get_forecast_accuracy_history(
    months: int = Query(6, ge=1, le=24),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get historical forecast vs actual comparison.
    Used to track forecast accuracy over time.
    """
    service = CashFlowForecastService(db)
    return await service.get_forecast_vs_actual(months=months)


# DSO Analysis Endpoints

@router.get("/dso/current")
async def get_current_dso(
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get current Days Sales Outstanding (DSO) calculation.
    Uses 30/60/90 day average sales methods.
    """
    service = DSOAnalysisService(db)
    return await service.calculate_current_dso()


@router.get("/dso/trend")
async def get_dso_trend(
    months: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get monthly DSO trend for the specified period.

    Args:
        months: Number of months of historical data (1-24)

    Returns:
        Monthly DSO values with trend data
    """
    service = DSOAnalysisService(db)
    return await service.get_dso_trend(months=months)


@router.get("/dso/by-segment")
async def get_dso_by_segment(
    segment_type: str = Query("salesperson", regex="^(salesperson|customer_type|branch)$"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get DSO broken down by business segment.

    Args:
        segment_type: Type of segmentation (salesperson, customer_type, branch)

    Returns:
        DSO for each segment with variance from target
    """
    service = DSOAnalysisService(db)
    return await service.get_dso_by_segment(segment_type=segment_type)


@router.get("/dso/alerts")
async def get_dso_alerts(
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get customers with DSO significantly above company average.
    Identifies problem accounts requiring attention.
    """
    service = DSOAnalysisService(db)
    return await service.get_dso_alerts()


# Collections Performance Endpoints

@router.get("/performance/summary")
async def get_collections_performance_summary(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get overall collections performance metrics.

    Args:
        days: Number of days to analyze (1-90)

    Returns:
        Summary metrics for collections team performance
    """
    from datetime import datetime, timedelta
    from sqlalchemy import select, func
    from src.models.note import Note
    from src.models.email_log import EmailLog
    from src.models.task import Task
    from src.models.payment import Payment

    start_date = datetime.now() - timedelta(days=days)

    # Count collection activities
    calls_result = await db.execute(
        select(func.count(Note.id)).where(
            Note.note_type == 'phone_call',
            Note.created_at >= start_date
        )
    )
    total_calls = calls_result.scalar() or 0

    emails_result = await db.execute(
        select(func.count(EmailLog.id)).where(
            EmailLog.email_type == 'reminder',
            EmailLog.sent_at >= start_date
        )
    )
    total_emails = emails_result.scalar() or 0

    promises_result = await db.execute(
        select(
            func.count(Note.id).label('total'),
            func.sum(func.cast(Note.promise_status == 'kept', int)).label('kept')
        ).where(
            Note.note_type == 'promise_to_pay',
            Note.created_at >= start_date
        )
    )
    promise_stats = promises_result.one()

    # Calculate collections amount
    payments_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.payment_date >= start_date.date()
        )
    )
    amount_collected = float(payments_result.scalar() or 0)

    # Tasks completed
    tasks_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.status == 'completed',
            Task.updated_at >= start_date
        )
    )
    tasks_completed = tasks_result.scalar() or 0

    return {
        "period_days": days,
        "activities": {
            "total_calls": total_calls,
            "total_emails": total_emails,
            "tasks_completed": tasks_completed
        },
        "promises": {
            "total": promise_stats.total or 0,
            "kept": promise_stats.kept or 0,
            "kept_rate": round((promise_stats.kept / promise_stats.total * 100), 1) if promise_stats.total > 0 else 0
        },
        "collections": {
            "amount_collected": amount_collected,
            "average_per_day": round(amount_collected / days, 2) if days > 0 else 0
        }
    }


@router.get("/performance/by-user")
async def get_performance_by_user(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get collections performance broken down by user.

    Args:
        days: Number of days to analyze (1-90)

    Returns:
        Performance metrics per user
    """
    from datetime import datetime, timedelta
    from sqlalchemy import select, func
    from src.models.user import User
    from src.models.note import Note
    from src.models.task import Task

    start_date = datetime.now() - timedelta(days=days)

    # Get users with activity
    users_result = await db.execute(
        select(User.id, User.full_name).where(
            User.role.in_(['ar_manager', 'ar_specialist']),
            User.is_active == True
        )
    )
    users = users_result.all()

    performance = []
    for user_id, user_name in users:
        # Count calls
        calls_result = await db.execute(
            select(func.count(Note.id)).where(
                Note.user_id == user_id,
                Note.note_type == 'phone_call',
                Note.created_at >= start_date
            )
        )
        calls = calls_result.scalar() or 0

        # Count tasks completed
        tasks_result = await db.execute(
            select(func.count(Task.id)).where(
                Task.assigned_to == user_id,
                Task.status == 'completed',
                Task.updated_at >= start_date
            )
        )
        tasks = tasks_result.scalar() or 0

        # Count promises logged
        promises_result = await db.execute(
            select(
                func.count(Note.id).label('total'),
                func.sum(func.cast(Note.promise_status == 'kept', int)).label('kept')
            ).where(
                Note.user_id == user_id,
                Note.note_type == 'promise_to_pay',
                Note.created_at >= start_date
            )
        )
        promise_stats = promises_result.one()

        performance.append({
            "user_id": user_id,
            "user_name": user_name,
            "calls_made": calls,
            "tasks_completed": tasks,
            "promises_logged": promise_stats.total or 0,
            "promises_kept": promise_stats.kept or 0,
            "promise_kept_rate": round((promise_stats.kept / promise_stats.total * 100), 1) if promise_stats.total > 0 else 0
        })

    # Sort by calls made descending
    performance.sort(key=lambda x: x['calls_made'], reverse=True)

    return performance


@router.get("/performance/trend")
async def get_performance_trend(
    weeks: int = Query(12, ge=1, le=52),
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """
    Get weekly collections performance trend.

    Args:
        weeks: Number of weeks of historical data (1-52)

    Returns:
        Weekly performance metrics
    """
    from datetime import datetime, timedelta
    from sqlalchemy import select, func, and_
    from src.models.note import Note
    from src.models.payment import Payment

    today = datetime.now().date()
    trends = []

    for week_offset in range(weeks, 0, -1):
        week_start = today - timedelta(weeks=week_offset)
        week_end = week_start + timedelta(days=6)

        # Calls made
        calls_result = await db.execute(
            select(func.count(Note.id)).where(
                Note.note_type == 'phone_call',
                func.date(Note.created_at) >= week_start,
                func.date(Note.created_at) <= week_end
            )
        )
        calls = calls_result.scalar() or 0

        # Payments collected
        payments_result = await db.execute(
            select(
                func.count(Payment.id).label('count'),
                func.sum(Payment.amount).label('total')
            ).where(
                Payment.payment_date >= week_start,
                Payment.payment_date <= week_end
            )
        )
        payment_stats = payments_result.one()

        trends.append({
            "week": weeks - week_offset + 1,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "calls_made": calls,
            "payments_count": payment_stats.count or 0,
            "amount_collected": float(payment_stats.total or 0)
        })

    return trends
