"""
Tasks API Routes - W01
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from src.db.connection import get_db
from src.models.task import Task
from src.models.customer import Customer

router = APIRouter()


class TaskCreate(BaseModel):
    customer_id: int
    invoice_id: Optional[int] = None
    task_type: str  # collection_call, follow_up, dispute_resolution, review
    description: Optional[str] = None
    due_at: datetime
    priority: int = 5


class TaskResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    invoice_id: Optional[int] = None
    task_type: str
    description: Optional[str] = None
    due_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    priority: int
    is_overdue: bool
    is_due_today: bool

    class Config:
        from_attributes = True


@router.get("/")
async def list_tasks(
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    customer_id: Optional[int] = None,
    overdue_only: bool = False,
    due_today: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List tasks with filtering"""
    query = select(Task, Customer.name).join(Customer)

    filters = []
    if status:
        filters.append(Task.status == status)
    if assigned_to:
        filters.append(Task.assigned_to_user_id == assigned_to)
    if customer_id:
        filters.append(Task.customer_id == customer_id)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Task.priority.desc(), Task.due_at.asc())
    result = await db.execute(query)
    rows = result.all()

    tasks = []
    for t, cname in rows:
        if overdue_only and not t.is_overdue:
            continue
        if due_today and not t.is_due_today:
            continue
        tasks.append(TaskResponse(
            id=t.id,
            customer_id=t.customer_id,
            customer_name=cname,
            invoice_id=t.invoice_id,
            task_type=t.task_type,
            description=t.description,
            due_at=t.due_at,
            completed_at=t.completed_at,
            status=t.status,
            priority=t.priority,
            is_overdue=t.is_overdue,
            is_due_today=t.is_due_today
        ))

    return tasks


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task"""
    # TODO: Get assigned_to from auth or param
    assigned_to = 1

    db_task = Task(
        customer_id=task.customer_id,
        invoice_id=task.invoice_id,
        assigned_to_user_id=assigned_to,
        task_type=task.task_type,
        description=task.description,
        due_at=task.due_at,
        priority=task.priority
    )

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    return db_task


@router.put("/{task_id}/complete")
async def complete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Mark task as completed"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "Completed"
    task.completed_at = datetime.now()
    await db.commit()

    return {"message": "Task completed"}


@router.put("/{task_id}/snooze")
async def snooze_task(
    task_id: int,
    new_due_at: datetime,
    db: AsyncSession = Depends(get_db)
):
    """Snooze task to a new date"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "Snoozed"
    task.due_at = new_due_at
    await db.commit()

    return {"message": f"Task snoozed to {new_due_at}"}
