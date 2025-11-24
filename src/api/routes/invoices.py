"""
Invoice API Routes - B03
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

from src.db.connection import get_db
from src.models.invoice import Invoice
from src.models.customer import Customer

router = APIRouter()


class InvoiceResponse(BaseModel):
    id: int
    epicor_invoice_number: str
    customer_id: int
    customer_name: Optional[str] = None
    invoice_date: date
    due_date: date
    original_amount: Decimal
    open_balance: Decimal
    status: str
    invoice_type: str
    days_past_due: int
    aging_bucket: str
    branch_id: Optional[str] = None
    department: Optional[str] = None
    salesperson_id: Optional[str] = None
    job_reference: Optional[str] = None
    po_reference: Optional[str] = None

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=InvoiceListResponse)
async def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    aging_bucket: Optional[str] = None,
    min_balance: Optional[float] = None,
    branch_id: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    past_due_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List invoices with filtering and pagination"""
    query = select(Invoice, Customer.name.label("customer_name")).join(Customer)
    count_query = select(func.count(Invoice.id))

    filters = []
    if customer_id:
        filters.append(Invoice.customer_id == customer_id)
    if status:
        filters.append(Invoice.status == status)
    if min_balance:
        filters.append(Invoice.open_balance >= min_balance)
    if branch_id:
        filters.append(Invoice.branch_id == branch_id)
    if salesperson_id:
        filters.append(Invoice.salesperson_id == salesperson_id)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Invoice.due_date.asc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    items = []
    for row in rows:
        inv = row[0]
        cust_name = row[1]
        # Filter by aging bucket and past_due in Python
        if aging_bucket and inv.aging_bucket != aging_bucket:
            continue
        if past_due_only and inv.days_past_due == 0:
            continue
        items.append(InvoiceResponse(
            id=inv.id,
            epicor_invoice_number=inv.epicor_invoice_number,
            customer_id=inv.customer_id,
            customer_name=cust_name,
            invoice_date=inv.invoice_date,
            due_date=inv.due_date,
            original_amount=inv.original_amount,
            open_balance=inv.open_balance,
            status=inv.status,
            invoice_type=inv.invoice_type,
            days_past_due=inv.days_past_due,
            aging_bucket=inv.aging_bucket,
            branch_id=inv.branch_id,
            department=inv.department,
            salesperson_id=inv.salesperson_id,
            job_reference=inv.job_reference,
            po_reference=inv.po_reference
        ))

    return InvoiceListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """Get invoice by ID"""
    result = await db.execute(
        select(Invoice, Customer.name)
        .join(Customer)
        .where(Invoice.id == invoice_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found")

    inv, cust_name = row
    return InvoiceResponse(
        id=inv.id,
        epicor_invoice_number=inv.epicor_invoice_number,
        customer_id=inv.customer_id,
        customer_name=cust_name,
        invoice_date=inv.invoice_date,
        due_date=inv.due_date,
        original_amount=inv.original_amount,
        open_balance=inv.open_balance,
        status=inv.status,
        invoice_type=inv.invoice_type,
        days_past_due=inv.days_past_due,
        aging_bucket=inv.aging_bucket,
        branch_id=inv.branch_id,
        department=inv.department,
        salesperson_id=inv.salesperson_id,
        job_reference=inv.job_reference,
        po_reference=inv.po_reference
    )


@router.get("/aging/summary")
async def get_aging_summary(
    branch_id: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get aging summary by bucket"""
    query = select(Invoice).where(Invoice.open_balance > 0)

    if branch_id:
        query = query.where(Invoice.branch_id == branch_id)
    if salesperson_id:
        query = query.where(Invoice.salesperson_id == salesperson_id)

    result = await db.execute(query)
    invoices = result.scalars().all()

    aging = {
        "current": {"count": 0, "amount": 0},
        "1-30": {"count": 0, "amount": 0},
        "31-60": {"count": 0, "amount": 0},
        "61-90": {"count": 0, "amount": 0},
        "90+": {"count": 0, "amount": 0}
    }

    for inv in invoices:
        bucket = inv.aging_bucket
        if bucket in aging:
            aging[bucket]["count"] += 1
            aging[bucket]["amount"] += float(inv.open_balance)

    total_ar = sum(a["amount"] for a in aging.values())
    total_past_due = total_ar - aging["current"]["amount"]

    return {
        "aging": aging,
        "total_ar": total_ar,
        "total_past_due": total_past_due,
        "total_invoices": sum(a["count"] for a in aging.values())
    }
