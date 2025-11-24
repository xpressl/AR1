"""
Notifications API Routes - Phase 2
Handles in-app notifications for users.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from src.db.connection import get_db
from src.models.notification import Notification

router = APIRouter()


class NotificationCreate(BaseModel):
    user_id: int
    notification_type: str
    title: str
    message: Optional[str] = None
    severity: str = "info"
    customer_id: Optional[int] = None
    alert_id: Optional[int] = None
    task_id: Optional[int] = None
    action_url: Optional[str] = None


class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: Optional[str]
    severity: str
    customer_id: Optional[int]
    action_url: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/")
async def get_notifications(
    user_id: int,
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get notifications for a user."""
    query = select(Notification).where(
        Notification.user_id == user_id,
        Notification.is_dismissed == False
    )

    if unread_only:
        query = query.where(Notification.is_read == False)

    if notification_type:
        query = query.where(Notification.notification_type == notification_type)

    query = query.order_by(Notification.created_at.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    notifications = result.scalars().all()

    return [
        {
            "id": n.id,
            "notification_type": n.notification_type,
            "title": n.title,
            "message": n.message,
            "severity": n.severity,
            "customer_id": n.customer_id,
            "alert_id": n.alert_id,
            "task_id": n.task_id,
            "action_url": n.action_url,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None
        }
        for n in notifications
    ]


@router.get("/count")
async def get_notification_count(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications (for badge display)."""
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_dismissed == False
        )
    )
    unread_count = result.scalar() or 0

    # Also get count by severity
    severity_result = await db.execute(
        select(
            Notification.severity,
            func.count(Notification.id)
        ).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_dismissed == False
        ).group_by(Notification.severity)
    )
    severity_counts = {row[0]: row[1] for row in severity_result.all()}

    return {
        "unread": unread_count,
        "critical": severity_counts.get("critical", 0),
        "warning": severity_counts.get("warning", 0),
        "info": severity_counts.get("info", 0)
    }


@router.post("/")
async def create_notification(
    notification: NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new notification."""
    db_notification = Notification(
        user_id=notification.user_id,
        notification_type=notification.notification_type,
        title=notification.title,
        message=notification.message,
        severity=notification.severity,
        customer_id=notification.customer_id,
        alert_id=notification.alert_id,
        task_id=notification.task_id,
        action_url=notification.action_url
    )

    db.add(db_notification)
    await db.commit()
    await db.refresh(db_notification)

    return {
        "id": db_notification.id,
        "message": "Notification created"
    }


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    notification.read_at = datetime.utcnow()
    await db.commit()

    return {"message": "Notification marked as read"}


@router.put("/mark-all-read")
async def mark_all_notifications_read(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read for a user."""
    await db.execute(
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        .values(is_read=True, read_at=datetime.utcnow())
    )
    await db.commit()

    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}")
async def dismiss_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Dismiss (soft delete) a notification."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_dismissed = True
    notification.dismissed_at = datetime.utcnow()
    await db.commit()

    return {"message": "Notification dismissed"}


@router.post("/broadcast")
async def broadcast_notification(
    notification_type: str,
    title: str,
    message: Optional[str] = None,
    severity: str = "info",
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Broadcast a notification to multiple users.
    If role is specified, sends only to users with that role.
    """
    from src.models.user import User

    query = select(User.id).where(User.is_active == True)
    if role:
        query = query.where(User.role == role)

    result = await db.execute(query)
    user_ids = [row[0] for row in result.all()]

    for user_id in user_ids:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            severity=severity
        )
        db.add(notification)

    await db.commit()

    return {
        "message": f"Notification sent to {len(user_ids)} users",
        "user_count": len(user_ids)
    }


class NotificationService:
    """Service for creating notifications from other parts of the system."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def notify_critical_alert(
        self,
        alert_id: int,
        customer_id: int,
        customer_name: str,
        alert_title: str
    ):
        """Create notifications for a new critical alert."""
        from src.models.user import User

        # Get AR team users
        result = await self.db.execute(
            select(User.id).where(
                User.role.in_(['ar_manager', 'ar_specialist']),
                User.is_active == True
            )
        )
        user_ids = [row[0] for row in result.all()]

        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                notification_type="alert",
                title=f"Critical Alert: {customer_name}",
                message=alert_title,
                severity="critical",
                customer_id=customer_id,
                alert_id=alert_id,
                action_url=f"/customers/{customer_id}"
            )
            self.db.add(notification)

        await self.db.commit()

    async def notify_broken_promise(
        self,
        customer_id: int,
        customer_name: str,
        promise_amount: float
    ):
        """Create notifications for a broken promise."""
        from src.models.user import User

        result = await self.db.execute(
            select(User.id).where(
                User.role.in_(['ar_manager', 'ar_specialist']),
                User.is_active == True
            )
        )
        user_ids = [row[0] for row in result.all()]

        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                notification_type="promise",
                title=f"Broken Promise: {customer_name}",
                message=f"Promise to pay ${promise_amount:,.2f} was not kept",
                severity="warning",
                customer_id=customer_id,
                action_url=f"/customers/{customer_id}"
            )
            self.db.add(notification)

        await self.db.commit()

    async def notify_task_due(
        self,
        user_id: int,
        task_id: int,
        task_title: str,
        customer_name: Optional[str] = None
    ):
        """Create notification for a task that's due."""
        notification = Notification(
            user_id=user_id,
            notification_type="task",
            title=f"Task Due: {task_title}",
            message=f"Task for {customer_name}" if customer_name else None,
            severity="info",
            task_id=task_id,
            action_url=f"/tasks/{task_id}"
        )
        self.db.add(notification)
        await self.db.commit()
