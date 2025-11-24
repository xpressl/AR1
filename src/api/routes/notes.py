"""
Notes API Routes - B05
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime

from src.db.connection import get_db
from src.models.note import Note

router = APIRouter()


class NoteCreate(BaseModel):
    customer_id: int
    invoice_id: Optional[int] = None
    note_type: str  # call, email, dispute, internal, promise_to_pay
    content: str
    promise_amount: Optional[Decimal] = None
    promise_date: Optional[date] = None


class NoteResponse(BaseModel):
    id: int
    customer_id: int
    invoice_id: Optional[int] = None
    user_id: int
    note_type: str
    content: str
    promise_amount: Optional[Decimal] = None
    promise_date: Optional[date] = None
    promise_status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=NoteResponse)
async def create_note(
    note: NoteCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new note"""
    # TODO: Get user_id from auth context
    user_id = 1  # Placeholder

    db_note = Note(
        customer_id=note.customer_id,
        invoice_id=note.invoice_id,
        user_id=user_id,
        note_type=note.note_type,
        content=note.content,
        promise_amount=note.promise_amount,
        promise_date=note.promise_date,
        promise_status="pending" if note.note_type == "promise_to_pay" else None
    )

    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)

    return db_note


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: AsyncSession = Depends(get_db)):
    """Get note by ID"""
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("/promises/pending")
async def get_pending_promises(db: AsyncSession = Depends(get_db)):
    """Get all pending promise-to-pay notes"""
    result = await db.execute(
        select(Note)
        .where(Note.note_type == "promise_to_pay")
        .where(Note.promise_status == "pending")
        .order_by(Note.promise_date.asc())
    )
    notes = result.scalars().all()

    return [
        {
            "id": n.id,
            "customer_id": n.customer_id,
            "promise_amount": float(n.promise_amount) if n.promise_amount else None,
            "promise_date": n.promise_date.isoformat() if n.promise_date else None,
            "content": n.content,
            "is_overdue": n.is_promise_due,
            "created_at": n.created_at.isoformat() if n.created_at else None
        }
        for n in notes
    ]


@router.put("/{note_id}/promise-status")
async def update_promise_status(
    note_id: int,
    status: str,  # kept, broken
    db: AsyncSession = Depends(get_db)
):
    """Update promise-to-pay status"""
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.note_type != "promise_to_pay":
        raise HTTPException(status_code=400, detail="Note is not a promise to pay")
    if status not in ["kept", "broken"]:
        raise HTTPException(status_code=400, detail="Status must be 'kept' or 'broken'")

    note.promise_status = status
    await db.commit()

    return {"message": f"Promise status updated to {status}"}
