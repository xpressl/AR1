"""
Customer API Routes - B02
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from decimal import Decimal

from src.db.connection import get_db
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.payment import Payment
from src.models.note import Note
from src.models.alert import Alert

router = APIRouter()


# Pydantic Schemas
class CustomerBase(BaseModel):
    epicor_customer_id: str
    name: str
    dba_trade_name: Optional[str] = None
    billing_email: Optional[str] = None
    billing_phone: Optional[str] = None
    primary_contact_name: Optional[str] = None
    salesperson_id: Optional[str] = None
    terms_code: Optional[str] = None
    credit_limit: Optional[Decimal] = 0
    status: str = "Active"
    customer_type: Optional[str] = None
    branch_id: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    current_balance: Decimal
    last_invoice_date: Optional[date] = None
    last_payment_date: Optional[date] = None
    credit_utilization: float
    is_inactive: bool
    is_over_credit_limit: bool
    is_near_credit_limit: bool
    days_since_last_invoice: Optional[int] = None

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    items: List[CustomerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class Customer360Response(BaseModel):
    customer: CustomerResponse
    aging: dict
    recent_invoices: List[dict]
    recent_payments: List[dict]
    recent_notes: List[dict]
    active_alerts: List[dict]
    open_tasks: List[dict]


# Endpoints

@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    branch_id: Optional[str] = None,
    has_balance: Optional[bool] = None,
    is_inactive: Optional[bool] = None,
    is_over_limit: Optional[bool] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    db: AsyncSession = Depends(get_db)
):
    """
    List customers with filtering and pagination.
    """
    # Build query
    query = select(Customer)
    count_query = select(func.count(Customer.id))

    # Apply filters
    filters = []
    if search:
        search_filter = or_(
            Customer.name.ilike(f"%{search}%"),
            Customer.epicor_customer_id.ilike(f"%{search}%"),
            Customer.primary_contact_name.ilike(f"%{search}%")
        )
        filters.append(search_filter)

    if status:
        filters.append(Customer.status == status)

    if salesperson_id:
        filters.append(Customer.salesperson_id == salesperson_id)

    if branch_id:
        filters.append(Customer.branch_id == branch_id)

    if has_balance:
        filters.append(Customer.current_balance > 0)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply sorting
    sort_column = getattr(Customer, sort_by, Customer.name)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    customers = result.scalars().all()

    # Filter inactive and over-limit in Python (computed properties)
    customer_list = []
    for c in customers:
        if is_inactive is not None and c.is_inactive != is_inactive:
            continue
        if is_over_limit is not None and c.is_over_credit_limit != is_over_limit:
            continue
        customer_list.append(CustomerResponse(
            id=c.id,
            epicor_customer_id=c.epicor_customer_id,
            name=c.name,
            dba_trade_name=c.dba_trade_name,
            billing_email=c.billing_email,
            billing_phone=c.billing_phone,
            primary_contact_name=c.primary_contact_name,
            salesperson_id=c.salesperson_id,
            terms_code=c.terms_code,
            credit_limit=c.credit_limit or 0,
            status=c.status,
            customer_type=c.customer_type,
            branch_id=c.branch_id,
            current_balance=c.current_balance or 0,
            last_invoice_date=c.last_invoice_date,
            last_payment_date=c.last_payment_date,
            credit_utilization=c.credit_utilization,
            is_inactive=c.is_inactive,
            is_over_credit_limit=c.is_over_credit_limit,
            is_near_credit_limit=c.is_near_credit_limit,
            days_since_last_invoice=c.days_since_last_invoice
        ))

    return CustomerListResponse(
        items=customer_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get customer by ID"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{customer_id}/360", response_model=Customer360Response)
async def get_customer_360(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete customer 360 view including:
    - Customer details
    - Aging breakdown
    - Recent invoices
    - Recent payments
    - Recent notes
    - Active alerts
    - Open tasks
    """
    # Get customer
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get invoices for aging
    invoices_result = await db.execute(
        select(Invoice)
        .where(Invoice.customer_id == customer_id)
        .where(Invoice.open_balance > 0)
        .order_by(Invoice.due_date.desc())
    )
    invoices = invoices_result.scalars().all()

    # Calculate aging
    aging = {"current": 0, "1-30": 0, "31-60": 0, "61-90": 0, "90+": 0}
    for inv in invoices:
        bucket = inv.aging_bucket
        aging[bucket] = aging.get(bucket, 0) + float(inv.open_balance)

    # Recent invoices (last 10)
    recent_invoices = [
        {
            "id": inv.id,
            "invoice_number": inv.epicor_invoice_number,
            "invoice_date": inv.invoice_date.isoformat(),
            "due_date": inv.due_date.isoformat(),
            "original_amount": float(inv.original_amount),
            "open_balance": float(inv.open_balance),
            "days_past_due": inv.days_past_due,
            "aging_bucket": inv.aging_bucket,
            "status": inv.status
        }
        for inv in invoices[:10]
    ]

    # Recent payments
    payments_result = await db.execute(
        select(Payment)
        .where(Payment.customer_id == customer_id)
        .order_by(Payment.payment_date.desc())
        .limit(10)
    )
    payments = payments_result.scalars().all()
    recent_payments = [
        {
            "id": p.id,
            "payment_date": p.payment_date.isoformat(),
            "amount": float(p.amount),
            "payment_type": p.payment_type,
            "check_number": p.check_number,
            "unapplied_amount": float(p.unapplied_amount or 0)
        }
        for p in payments
    ]

    # Recent notes
    notes_result = await db.execute(
        select(Note)
        .where(Note.customer_id == customer_id)
        .order_by(Note.created_at.desc())
        .limit(20)
    )
    notes = notes_result.scalars().all()
    recent_notes = [
        {
            "id": n.id,
            "note_type": n.note_type,
            "content": n.content,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "promise_amount": float(n.promise_amount) if n.promise_amount else None,
            "promise_date": n.promise_date.isoformat() if n.promise_date else None,
            "promise_status": n.promise_status
        }
        for n in notes
    ]

    # Active alerts
    alerts_result = await db.execute(
        select(Alert)
        .where(Alert.customer_id == customer_id)
        .where(Alert.is_active == True)
        .order_by(Alert.severity.desc(), Alert.triggered_at.desc())
    )
    alerts = alerts_result.scalars().all()
    active_alerts = [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "triggered_at": a.triggered_at.isoformat() if a.triggered_at else None,
            "css_class": a.css_class,
            "icon": a.icon
        }
        for a in alerts
    ]

    return Customer360Response(
        customer=customer,
        aging=aging,
        recent_invoices=recent_invoices,
        recent_payments=recent_payments,
        recent_notes=recent_notes,
        active_alerts=active_alerts,
        open_tasks=[]  # TODO: Add tasks query
    )


@router.get("/{customer_id}/invoices")
async def get_customer_invoices(
    customer_id: int,
    status: Optional[str] = None,
    aging_bucket: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all invoices for a customer"""
    query = select(Invoice).where(Invoice.customer_id == customer_id)

    if status:
        query = query.where(Invoice.status == status)

    query = query.order_by(Invoice.due_date.desc())
    result = await db.execute(query)
    invoices = result.scalars().all()

    # Filter by aging bucket in Python (computed property)
    if aging_bucket:
        invoices = [inv for inv in invoices if inv.aging_bucket == aging_bucket]

    return [
        {
            "id": inv.id,
            "invoice_number": inv.epicor_invoice_number,
            "invoice_date": inv.invoice_date.isoformat(),
            "due_date": inv.due_date.isoformat(),
            "original_amount": float(inv.original_amount),
            "open_balance": float(inv.open_balance),
            "days_past_due": inv.days_past_due,
            "aging_bucket": inv.aging_bucket,
            "status": inv.status,
            "invoice_type": inv.invoice_type
        }
        for inv in invoices
    ]


@router.get("/{customer_id}/payments")
async def get_customer_payments(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all payments for a customer"""
    result = await db.execute(
        select(Payment)
        .where(Payment.customer_id == customer_id)
        .order_by(Payment.payment_date.desc())
    )
    payments = result.scalars().all()

    return [
        {
            "id": p.id,
            "payment_id": p.epicor_payment_id,
            "payment_date": p.payment_date.isoformat(),
            "amount": float(p.amount),
            "payment_type": p.payment_type,
            "check_number": p.check_number,
            "reference_number": p.reference_number,
            "unapplied_amount": float(p.unapplied_amount or 0)
        }
        for p in payments
    ]


@router.get("/{customer_id}/notes")
async def get_customer_notes(
    customer_id: int,
    note_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all notes for a customer"""
    query = select(Note).where(Note.customer_id == customer_id)

    if note_type:
        query = query.where(Note.note_type == note_type)

    query = query.order_by(Note.created_at.desc())
    result = await db.execute(query)
    notes = result.scalars().all()

    return [
        {
            "id": n.id,
            "note_type": n.note_type,
            "content": n.content,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "promise_amount": float(n.promise_amount) if n.promise_amount else None,
            "promise_date": n.promise_date.isoformat() if n.promise_date else None,
            "promise_status": n.promise_status
        }
        for n in notes
    ]


@router.get("/{customer_id}/alerts")
async def get_customer_alerts(
    customer_id: int,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get alerts for a customer"""
    query = select(Alert).where(Alert.customer_id == customer_id)

    if active_only:
        query = query.where(Alert.is_active == True)

    query = query.order_by(Alert.severity.desc(), Alert.triggered_at.desc())
    result = await db.execute(query)
    alerts = result.scalars().all()

    return [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "is_active": a.is_active,
            "triggered_at": a.triggered_at.isoformat() if a.triggered_at else None,
            "css_class": a.css_class,
            "icon": a.icon
        }
        for a in alerts
    ]
