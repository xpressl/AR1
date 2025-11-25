"""
Batch Operations API Routes

Bulk/batch operations on multiple records
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from pydantic import BaseModel

from src.db.connection import get_db
from src.services.batch.batch_service import BatchService
from src.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/batch", tags=["batch"])


# Request models
class BulkEmailRequest(BaseModel):
    customer_ids: List[str]
    template_id: str
    subject: str
    body: str


class BulkTaskRequest(BaseModel):
    customer_ids: List[str]
    task_type: str
    description: str
    assigned_to: str
    due_date: datetime


class BulkStatusRequest(BaseModel):
    customer_ids: List[str]
    status: str


class BulkNoteRequest(BaseModel):
    customer_ids: List[str]
    note_content: str
    note_type: str


@router.post("/send-emails")
async def send_bulk_emails(
    request: BulkEmailRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send emails to multiple customers.

    Requires:
    - customer_ids: List of customer IDs
    - template_id: Email template ID
    - subject: Email subject (with variables substituted)
    - body: Email body (with variables substituted)

    Returns batch operation ID and status.
    """
    if not request.customer_ids:
        raise HTTPException(status_code=400, detail="customer_ids is required")

    if len(request.customer_ids) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 customers per batch")

    batch_service = BatchService(db)

    try:
        result = await batch_service.send_bulk_emails(
            customer_ids=request.customer_ids,
            template_id=request.template_id,
            user_id=current_user['id'],
            subject=request.subject,
            body=request.body
        )

        return {
            'success': True,
            'batch_id': result['batch_id'],
            'total': result['total'],
            'successful': result['successful'],
            'failed': result['failed'],
            'errors': result['errors']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign-tasks")
async def assign_bulk_tasks(
    request: BulkTaskRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create tasks for multiple customers.

    Requires:
    - customer_ids: List of customer IDs
    - task_type: Type of task (follow_up, dispute, etc.)
    - description: Task description
    - assigned_to: User ID to assign tasks to
    - due_date: Task due date

    Returns batch operation ID and created task IDs.
    """
    if not request.customer_ids:
        raise HTTPException(status_code=400, detail="customer_ids is required")

    if len(request.customer_ids) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 customers per batch")

    batch_service = BatchService(db)

    try:
        result = await batch_service.assign_bulk_tasks(
            customer_ids=request.customer_ids,
            task_type=request.task_type,
            description=request.description,
            assigned_to=request.assigned_to,
            due_date=request.due_date,
            user_id=current_user['id']
        )

        return {
            'success': True,
            'batch_id': result['batch_id'],
            'total': result['total'],
            'successful': result['successful'],
            'failed': result['failed'],
            'created_tasks': result['created_tasks'],
            'errors': result['errors']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-status")
async def update_bulk_status(
    request: BulkStatusRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update status for multiple customers.

    Requires:
    - customer_ids: List of customer IDs
    - status: New status value

    Returns batch operation ID and count of updated records.
    """
    if not request.customer_ids:
        raise HTTPException(status_code=400, detail="customer_ids is required")

    if len(request.customer_ids) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 customers per batch")

    # Validate status
    valid_statuses = ['Active', 'Inactive', 'On Hold', 'Closed']
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    batch_service = BatchService(db)

    try:
        result = await batch_service.update_bulk_status(
            customer_ids=request.customer_ids,
            status=request.status,
            user_id=current_user['id']
        )

        return {
            'success': True,
            'batch_id': result['batch_id'],
            'total': result['total'],
            'updated': result['updated']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-notes")
async def add_bulk_notes(
    request: BulkNoteRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add same note to multiple customers.

    Requires:
    - customer_ids: List of customer IDs
    - note_content: Note text
    - note_type: Type of note (call, email, meeting, general)

    Returns batch operation ID and created note IDs.
    """
    if not request.customer_ids:
        raise HTTPException(status_code=400, detail="customer_ids is required")

    if len(request.customer_ids) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 customers per batch")

    # Validate note type
    valid_note_types = ['call', 'email', 'meeting', 'general']
    if request.note_type not in valid_note_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid note_type. Must be one of: {', '.join(valid_note_types)}"
        )

    batch_service = BatchService(db)

    try:
        result = await batch_service.add_bulk_notes(
            customer_ids=request.customer_ids,
            note_content=request.note_content,
            note_type=request.note_type,
            user_id=current_user['id']
        )

        return {
            'success': True,
            'batch_id': result['batch_id'],
            'total': result['total'],
            'successful': result['successful'],
            'failed': result['failed'],
            'created_notes': result['created_notes'],
            'errors': result['errors']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{batch_id}")
async def get_batch_status(
    batch_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of a batch operation.

    Returns:
    - Batch operation details
    - Progress percentage
    - Success rate
    - Error log (if any)
    """
    batch_service = BatchService(db)

    try:
        status = await batch_service.get_batch_status(batch_id)
        return status

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
