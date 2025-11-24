"""
Alerts API Routes - A01
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.db.connection import get_db
from src.models.alert import Alert, AlertType, AlertSeverity
from src.models.customer import Customer

router = APIRouter()


class AlertResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    invoice_id: Optional[int] = None
    alert_type: str
    severity: str
    message: Optional[str] = None
    is_active: bool
    triggered_at: datetime
    css_class: str
    icon: str

    class Config:
        from_attributes = True


class AlertSummary(BaseModel):
    critical: int
    high: int
    medium: int
    low: int
    total: int
    by_type: dict


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    active_only: bool = True,
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    customer_id: Optional[int] = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List alerts with filtering"""
    query = select(Alert, Customer.name).join(Customer)

    filters = []
    if active_only:
        filters.append(Alert.is_active == True)
    if severity:
        filters.append(Alert.severity == severity)
    if alert_type:
        filters.append(Alert.alert_type == alert_type)
    if customer_id:
        filters.append(Alert.customer_id == customer_id)

    if filters:
        query = query.where(and_(*filters))

    # Order by severity (Critical first) then by date
    query = query.order_by(
        Alert.severity.desc(),
        Alert.triggered_at.desc()
    ).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    return [
        AlertResponse(
            id=a.id,
            customer_id=a.customer_id,
            customer_name=cname,
            invoice_id=a.invoice_id,
            alert_type=a.alert_type,
            severity=a.severity,
            message=a.message,
            is_active=a.is_active,
            triggered_at=a.triggered_at,
            css_class=a.css_class,
            icon=a.icon
        )
        for a, cname in rows
    ]


@router.get("/summary", response_model=AlertSummary)
async def get_alerts_summary(db: AsyncSession = Depends(get_db)):
    """Get summary of active alerts"""
    result = await db.execute(
        select(Alert).where(Alert.is_active == True)
    )
    alerts = result.scalars().all()

    by_severity = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    by_type = {}

    for a in alerts:
        by_severity[a.severity] = by_severity.get(a.severity, 0) + 1
        by_type[a.alert_type] = by_type.get(a.alert_type, 0) + 1

    return AlertSummary(
        critical=by_severity["Critical"],
        high=by_severity["High"],
        medium=by_severity["Medium"],
        low=by_severity["Low"],
        total=len(alerts),
        by_type=by_type
    )


@router.get("/critical")
async def get_critical_alerts(db: AsyncSession = Depends(get_db)):
    """Get all critical alerts (for blinking display)"""
    result = await db.execute(
        select(Alert, Customer.name)
        .join(Customer)
        .where(Alert.is_active == True)
        .where(Alert.severity == "Critical")
        .order_by(Alert.triggered_at.desc())
    )
    rows = result.all()

    return [
        {
            "id": a.id,
            "customer_id": a.customer_id,
            "customer_name": cname,
            "alert_type": a.alert_type,
            "message": a.message,
            "triggered_at": a.triggered_at.isoformat(),
            "css_class": "alert-critical-pulse",  # Blinking class
            "icon": a.icon
        }
        for a, cname in rows
    ]


@router.put("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    resolution_note: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Resolve an alert"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_active = False
    alert.resolved_at = datetime.now()
    alert.resolution_note = resolution_note
    # TODO: resolved_by_user_id from auth

    await db.commit()
    return {"message": "Alert resolved"}


@router.get("/types")
async def get_alert_types():
    """Get all alert types"""
    return {
        "types": [t.value for t in AlertType],
        "severities": [s.value for s in AlertSeverity]
    }
