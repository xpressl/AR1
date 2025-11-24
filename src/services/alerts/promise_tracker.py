"""
Promise Tracker - A04
Tracks promise-to-pay notes and detects broken promises.
"""
from datetime import date, timedelta
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.note import Note
from src.models.customer import Customer


class PromiseTracker:
    """
    Tracks promise-to-pay commitments and identifies broken promises.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pending_promises(self) -> List[Dict]:
        """Get all pending promises"""
        result = await self.db.execute(
            select(Note, Customer.name)
            .join(Customer, Note.customer_id == Customer.id)
            .where(Note.note_type == "promise_to_pay")
            .where(Note.promise_status == "pending")
            .order_by(Note.promise_date.asc())
        )
        rows = result.all()

        promises = []
        for note, customer_name in rows:
            is_overdue = note.promise_date < date.today() if note.promise_date else False
            days_until = (note.promise_date - date.today()).days if note.promise_date else None

            promises.append({
                "note_id": note.id,
                "customer_id": note.customer_id,
                "customer_name": customer_name,
                "promise_amount": float(note.promise_amount) if note.promise_amount else None,
                "promise_date": note.promise_date.isoformat() if note.promise_date else None,
                "days_until_due": days_until,
                "is_overdue": is_overdue,
                "content": note.content,
                "created_at": note.created_at.isoformat() if note.created_at else None
            })

        return promises

    async def get_due_today(self) -> List[Dict]:
        """Get promises due today"""
        promises = await self.get_pending_promises()
        return [p for p in promises if p["days_until_due"] == 0]

    async def get_due_this_week(self) -> List[Dict]:
        """Get promises due this week"""
        promises = await self.get_pending_promises()
        return [p for p in promises if p["days_until_due"] is not None and 0 <= p["days_until_due"] <= 7]

    async def get_overdue(self) -> List[Dict]:
        """Get overdue promises (broken)"""
        promises = await self.get_pending_promises()
        return [p for p in promises if p["is_overdue"]]

    async def get_broken_promises(self) -> List[Dict]:
        """Get promises marked as broken"""
        result = await self.db.execute(
            select(Note, Customer.name)
            .join(Customer, Note.customer_id == Customer.id)
            .where(Note.note_type == "promise_to_pay")
            .where(Note.promise_status == "broken")
            .order_by(Note.promise_date.desc())
        )
        rows = result.all()

        return [
            {
                "note_id": note.id,
                "customer_id": note.customer_id,
                "customer_name": customer_name,
                "promise_amount": float(note.promise_amount) if note.promise_amount else None,
                "promise_date": note.promise_date.isoformat() if note.promise_date else None,
                "content": note.content
            }
            for note, customer_name in rows
        ]

    async def mark_as_broken(self, note_id: int) -> bool:
        """Mark a promise as broken"""
        result = await self.db.execute(
            select(Note).where(Note.id == note_id)
        )
        note = result.scalar_one_or_none()

        if note and note.note_type == "promise_to_pay":
            note.promise_status = "broken"
            await self.db.commit()
            return True
        return False

    async def mark_as_kept(self, note_id: int) -> bool:
        """Mark a promise as kept"""
        result = await self.db.execute(
            select(Note).where(Note.id == note_id)
        )
        note = result.scalar_one_or_none()

        if note and note.note_type == "promise_to_pay":
            note.promise_status = "kept"
            await self.db.commit()
            return True
        return False

    async def get_summary(self) -> Dict:
        """Get promise tracking summary"""
        pending = await self.get_pending_promises()
        overdue = [p for p in pending if p["is_overdue"]]
        due_today = [p for p in pending if p["days_until_due"] == 0]
        due_this_week = [p for p in pending if p["days_until_due"] is not None and 0 < p["days_until_due"] <= 7]

        return {
            "total_pending": len(pending),
            "total_pending_amount": sum(p["promise_amount"] or 0 for p in pending),
            "overdue": {
                "count": len(overdue),
                "amount": sum(p["promise_amount"] or 0 for p in overdue)
            },
            "due_today": {
                "count": len(due_today),
                "amount": sum(p["promise_amount"] or 0 for p in due_today)
            },
            "due_this_week": {
                "count": len(due_this_week),
                "amount": sum(p["promise_amount"] or 0 for p in due_this_week)
            }
        }
