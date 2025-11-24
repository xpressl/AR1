"""
Email API Routes - W03
Handles email sending and logging endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

from src.db.connection import get_db
from src.models.email_log import EmailLog
from src.services.email.email_service import EmailService

router = APIRouter()


# Pydantic Models
class SendEmailRequest(BaseModel):
    customer_id: int
    to_email: EmailStr
    cc_email: Optional[str] = None
    subject: str
    body: str
    template_id: Optional[str] = None
    attach_statement: bool = False
    attach_invoice_ids: Optional[List[int]] = None


class SendReminderRequest(BaseModel):
    customer_id: int
    reminder_type: str = "gentle"  # gentle, firm
    invoice_ids: Optional[List[int]] = None


class SendStatementRequest(BaseModel):
    customer_id: int
    attach_pdf: bool = True


class EmailLogResponse(BaseModel):
    id: int
    customer_id: Optional[int]
    to_email: str
    subject: str
    template_id: Optional[str]
    email_type: Optional[str]
    status: str
    sent_at: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Endpoints

@router.post("/send")
async def send_custom_email(
    request: SendEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a custom email to a customer."""
    email_service = EmailService(db)

    # Create HTML body (wrap plain text in basic HTML)
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    {request.body.replace(chr(10), '<br>')}
    </body>
    </html>
    """

    result = await email_service.send_email(
        to_email=request.to_email,
        subject=request.subject,
        body_html=body_html,
        cc=request.cc_email,
        customer_id=request.customer_id
    )

    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))

    return result


@router.post("/reminder")
async def send_reminder_email(
    request: SendReminderRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a payment reminder email."""
    if request.reminder_type not in ["gentle", "firm"]:
        raise HTTPException(status_code=400, detail="Invalid reminder type. Use 'gentle' or 'firm'")

    email_service = EmailService(db)
    result = await email_service.send_reminder(
        customer_id=request.customer_id,
        reminder_type=request.reminder_type,
        invoice_ids=request.invoice_ids
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


@router.post("/statement")
async def send_statement_email(
    request: SendStatementRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send an account statement email."""
    email_service = EmailService(db)
    result = await email_service.send_statement(
        customer_id=request.customer_id,
        attach_pdf=request.attach_pdf
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


@router.get("/log")
async def get_email_log(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    email_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get email log with optional filters."""
    query = select(EmailLog)

    if customer_id:
        query = query.where(EmailLog.customer_id == customer_id)
    if status:
        query = query.where(EmailLog.status == status)
    if email_type:
        query = query.where(EmailLog.email_type == email_type)

    query = query.order_by(EmailLog.created_at.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "customer_id": log.customer_id,
            "to_email": log.to_email,
            "subject": log.subject,
            "template_id": log.template_id,
            "email_type": log.email_type,
            "status": log.status,
            "sent_at": log.sent_at.isoformat() if log.sent_at else None,
            "opened_at": log.opened_at.isoformat() if log.opened_at else None,
            "created_at": log.created_at.isoformat() if log.created_at else None,
            "error": log.error_message
        }
        for log in logs
    ]


@router.get("/log/{log_id}")
async def get_email_log_detail(
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed email log entry."""
    result = await db.execute(
        select(EmailLog).where(EmailLog.id == log_id)
    )
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Email log not found")

    return {
        "id": log.id,
        "customer_id": log.customer_id,
        "invoice_id": log.invoice_id,
        "to_email": log.to_email,
        "cc_email": log.cc_email,
        "subject": log.subject,
        "template_id": log.template_id,
        "email_type": log.email_type,
        "status": log.status,
        "error_message": log.error_message,
        "sent_at": log.sent_at.isoformat() if log.sent_at else None,
        "opened_at": log.opened_at.isoformat() if log.opened_at else None,
        "clicked_at": log.clicked_at.isoformat() if log.clicked_at else None,
        "bounced_at": log.bounced_at.isoformat() if log.bounced_at else None,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "created_by": log.created_by
    }


@router.get("/stats")
async def get_email_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get email statistics for the specified period."""
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(days=days)

    # Get counts by status
    status_query = select(
        EmailLog.status,
        func.count(EmailLog.id).label('count')
    ).where(
        EmailLog.created_at >= cutoff
    ).group_by(EmailLog.status)

    status_result = await db.execute(status_query)
    status_counts = {row.status: row.count for row in status_result}

    # Get counts by type
    type_query = select(
        EmailLog.email_type,
        func.count(EmailLog.id).label('count')
    ).where(
        EmailLog.created_at >= cutoff
    ).group_by(EmailLog.email_type)

    type_result = await db.execute(type_query)
    type_counts = {row.email_type or "unknown": row.count for row in type_result}

    # Calculate totals and rates
    total = sum(status_counts.values())
    sent = status_counts.get("sent", 0)
    failed = status_counts.get("failed", 0)

    # Get open rate (if tracking is enabled)
    opened_query = select(func.count(EmailLog.id)).where(
        EmailLog.created_at >= cutoff,
        EmailLog.opened_at.isnot(None)
    )
    opened_result = await db.execute(opened_query)
    opened = opened_result.scalar() or 0

    return {
        "period_days": days,
        "total_emails": total,
        "by_status": status_counts,
        "by_type": type_counts,
        "sent_count": sent,
        "failed_count": failed,
        "opened_count": opened,
        "success_rate": round(sent / total * 100, 1) if total > 0 else 0,
        "open_rate": round(opened / sent * 100, 1) if sent > 0 else 0
    }


@router.get("/templates")
async def get_email_templates():
    """Get list of available email templates."""
    return [
        {
            "id": "reminder_gentle",
            "name": "Gentle Reminder",
            "description": "Friendly payment reminder for first contact",
            "variables": ["contact_name", "total_due", "due_date", "invoices"]
        },
        {
            "id": "reminder_firm",
            "name": "Firm Reminder",
            "description": "Urgent payment notice for significantly past due accounts",
            "variables": ["contact_name", "past_due_amount", "max_days_overdue", "invoices"]
        },
        {
            "id": "statement",
            "name": "Account Statement",
            "description": "Complete account statement with aging summary",
            "variables": ["customer_name", "aging_current", "aging_1_30", "aging_31_60", "aging_61_plus", "invoices"]
        }
    ]
