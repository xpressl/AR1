"""
Batch Service

Handles bulk/batch operations on multiple records
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import json

from src.models import (
    Customer, Note, Task, Alert, BatchOperation, EmailLog
)


class BatchService:
    """Service for performing batch operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_bulk_emails(
        self,
        customer_ids: List[str],
        template_id: str,
        user_id: str,
        subject: str,
        body: str
    ) -> Dict[str, Any]:
        """
        Send emails to multiple customers using a template.

        Args:
            customer_ids: List of customer IDs to email
            template_id: Email template ID
            user_id: User ID initiating the batch
            subject: Email subject (after variable substitution)
            body: Email body (after variable substitution)

        Returns:
            Batch operation result
        """
        # Create batch operation record
        batch_op = BatchOperation(
            operation_type="send_bulk_emails",
            description=f"Send email to {len(customer_ids)} customers",
            total_records=len(customer_ids),
            initiated_by=user_id,
            status="in_progress"
        )
        self.db.add(batch_op)
        await self.db.commit()
        await self.db.refresh(batch_op)

        successful = 0
        failed = 0
        errors = []

        try:
            for customer_id in customer_ids:
                try:
                    # Get customer
                    query = select(Customer).where(Customer.id == customer_id)
                    result = await self.db.execute(query)
                    customer = result.scalar_one_or_none()

                    if not customer or not customer.contact_email:
                        failed += 1
                        errors.append({
                            'customer_id': customer_id,
                            'error': 'No email address'
                        })
                        continue

                    # Substitute variables in subject and body
                    customer_subject = self._substitute_variables(
                        subject,
                        customer=customer
                    )
                    customer_body = self._substitute_variables(
                        body,
                        customer=customer
                    )

                    # Send email (using email service)
                    # TODO: Integrate with actual email service
                    # For now, just log it

                    email_log = EmailLog(
                        recipient_email=customer.contact_email,
                        subject=customer_subject,
                        body=customer_body,
                        status="sent",
                        sent_by=user_id
                    )
                    self.db.add(email_log)

                    successful += 1

                except Exception as e:
                    failed += 1
                    errors.append({
                        'customer_id': customer_id,
                        'error': str(e)
                    })

                # Update progress
                batch_op.processed_records += 1
                batch_op.successful_records = successful
                batch_op.failed_records = failed
                await self.db.commit()

            # Mark batch as completed
            batch_op.status = "completed"
            batch_op.completed_at = datetime.utcnow()
            batch_op.error_log = json.dumps(errors) if errors else None
            batch_op.result_summary = json.dumps({
                'successful': successful,
                'failed': failed,
                'template_id': template_id
            })

            await self.db.commit()

            return {
                'batch_id': str(batch_op.id),
                'total': len(customer_ids),
                'successful': successful,
                'failed': failed,
                'errors': errors
            }

        except Exception as e:
            # Mark batch as failed
            batch_op.status = "failed"
            batch_op.completed_at = datetime.utcnow()
            batch_op.error_log = json.dumps({'error': str(e)})
            await self.db.commit()

            raise

    async def assign_bulk_tasks(
        self,
        customer_ids: List[str],
        task_type: str,
        description: str,
        assigned_to: str,
        due_date: datetime,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Create tasks for multiple customers.

        Args:
            customer_ids: List of customer IDs
            task_type: Type of task
            description: Task description
            assigned_to: User ID to assign to
            due_date: Task due date
            user_id: User ID initiating the batch

        Returns:
            Batch operation result
        """
        # Create batch operation record
        batch_op = BatchOperation(
            operation_type="assign_bulk_tasks",
            description=f"Create tasks for {len(customer_ids)} customers",
            total_records=len(customer_ids),
            initiated_by=user_id,
            status="in_progress"
        )
        self.db.add(batch_op)
        await self.db.commit()
        await self.db.refresh(batch_op)

        successful = 0
        failed = 0
        errors = []
        created_tasks = []

        try:
            for customer_id in customer_ids:
                try:
                    # Verify customer exists
                    query = select(Customer).where(Customer.id == customer_id)
                    result = await self.db.execute(query)
                    customer = result.scalar_one_or_none()

                    if not customer:
                        failed += 1
                        errors.append({
                            'customer_id': customer_id,
                            'error': 'Customer not found'
                        })
                        continue

                    # Create task
                    task = Task(
                        customer_id=customer_id,
                        task_type=task_type,
                        description=description,
                        assigned_to=assigned_to,
                        due_date=due_date,
                        priority="medium",
                        status="pending"
                    )
                    self.db.add(task)
                    await self.db.flush()  # Get task ID

                    created_tasks.append(str(task.id))
                    successful += 1

                except Exception as e:
                    failed += 1
                    errors.append({
                        'customer_id': customer_id,
                        'error': str(e)
                    })

                # Update progress
                batch_op.processed_records += 1
                batch_op.successful_records = successful
                batch_op.failed_records = failed
                await self.db.commit()

            # Mark batch as completed
            batch_op.status = "completed"
            batch_op.completed_at = datetime.utcnow()
            batch_op.error_log = json.dumps(errors) if errors else None
            batch_op.result_summary = json.dumps({
                'successful': successful,
                'failed': failed,
                'created_tasks': created_tasks
            })

            await self.db.commit()

            return {
                'batch_id': str(batch_op.id),
                'total': len(customer_ids),
                'successful': successful,
                'failed': failed,
                'created_tasks': created_tasks,
                'errors': errors
            }

        except Exception as e:
            # Mark batch as failed
            batch_op.status = "failed"
            batch_op.completed_at = datetime.utcnow()
            batch_op.error_log = json.dumps({'error': str(e)})
            await self.db.commit()

            raise

    async def update_bulk_status(
        self,
        customer_ids: List[str],
        status: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Update status for multiple customers.

        Args:
            customer_ids: List of customer IDs
            status: New status value
            user_id: User ID initiating the batch

        Returns:
            Batch operation result
        """
        # Create batch operation record
        batch_op = BatchOperation(
            operation_type="update_bulk_status",
            description=f"Update status to '{status}' for {len(customer_ids)} customers",
            total_records=len(customer_ids),
            initiated_by=user_id,
            status="in_progress"
        )
        self.db.add(batch_op)
        await self.db.commit()
        await self.db.refresh(batch_op)

        try:
            # Update customers
            update_query = update(Customer).where(
                Customer.id.in_(customer_ids)
            ).values(
                status=status
            )

            result = await self.db.execute(update_query)
            updated_count = result.rowcount

            # Mark batch as completed
            batch_op.status = "completed"
            batch_op.completed_at = datetime.utcnow()
            batch_op.processed_records = updated_count
            batch_op.successful_records = updated_count
            batch_op.failed_records = 0
            batch_op.result_summary = json.dumps({
                'updated_count': updated_count,
                'new_status': status
            })

            await self.db.commit()

            return {
                'batch_id': str(batch_op.id),
                'total': len(customer_ids),
                'updated': updated_count
            }

        except Exception as e:
            # Mark batch as failed
            batch_op.status = "failed"
            batch_op.completed_at = datetime.utcnow()
            batch_op.error_log = json.dumps({'error': str(e)})
            await self.db.commit()

            raise

    async def add_bulk_notes(
        self,
        customer_ids: List[str],
        note_content: str,
        note_type: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Add same note to multiple customers.

        Args:
            customer_ids: List of customer IDs
            note_content: Note content
            note_type: Type of note (call, email, meeting, general)
            user_id: User ID initiating the batch

        Returns:
            Batch operation result
        """
        # Create batch operation record
        batch_op = BatchOperation(
            operation_type="add_bulk_notes",
            description=f"Add note to {len(customer_ids)} customers",
            total_records=len(customer_ids),
            initiated_by=user_id,
            status="in_progress"
        )
        self.db.add(batch_op)
        await self.db.commit()
        await self.db.refresh(batch_op)

        successful = 0
        failed = 0
        errors = []
        created_notes = []

        try:
            for customer_id in customer_ids:
                try:
                    # Verify customer exists
                    query = select(Customer).where(Customer.id == customer_id)
                    result = await self.db.execute(query)
                    customer = result.scalar_one_or_none()

                    if not customer:
                        failed += 1
                        errors.append({
                            'customer_id': customer_id,
                            'error': 'Customer not found'
                        })
                        continue

                    # Create note
                    note = Note(
                        customer_id=customer_id,
                        content=note_content,
                        note_type=note_type,
                        created_by=user_id
                    )
                    self.db.add(note)
                    await self.db.flush()  # Get note ID

                    created_notes.append(str(note.id))
                    successful += 1

                except Exception as e:
                    failed += 1
                    errors.append({
                        'customer_id': customer_id,
                        'error': str(e)
                    })

                # Update progress
                batch_op.processed_records += 1
                batch_op.successful_records = successful
                batch_op.failed_records = failed
                await self.db.commit()

            # Mark batch as completed
            batch_op.status = "completed"
            batch_op.completed_at = datetime.utcnow()
            batch_op.error_log = json.dumps(errors) if errors else None
            batch_op.result_summary = json.dumps({
                'successful': successful,
                'failed': failed,
                'created_notes': created_notes
            })

            await self.db.commit()

            return {
                'batch_id': str(batch_op.id),
                'total': len(customer_ids),
                'successful': successful,
                'failed': failed,
                'created_notes': created_notes,
                'errors': errors
            }

        except Exception as e:
            # Mark batch as failed
            batch_op.status = "failed"
            batch_op.completed_at = datetime.utcnow()
            batch_op.error_log = json.dumps({'error': str(e)})
            await self.db.commit()

            raise

    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Get status of a batch operation.

        Args:
            batch_id: Batch operation ID

        Returns:
            Batch operation status
        """
        query = select(BatchOperation).where(BatchOperation.id == batch_id)
        result = await self.db.execute(query)
        batch_op = result.scalar_one_or_none()

        if not batch_op:
            raise ValueError(f"Batch operation {batch_id} not found")

        return batch_op.to_dict()

    def _substitute_variables(
        self,
        text: str,
        customer: Customer,
        invoice: Optional[Any] = None
    ) -> str:
        """
        Substitute template variables with actual values.

        Supported variables:
            {{customer_name}}, {{balance}}, {{invoice_number}}, {{due_date}}, etc.
        """
        replacements = {
            '{{customer_name}}': customer.name or '',
            '{{customer_id}}': str(customer.id) or '',
            '{{balance}}': f"${customer.balance or 0:,.2f}",
            '{{credit_limit}}': f"${customer.credit_limit or 0:,.2f}",
            '{{contact_email}}': customer.contact_email or '',
            '{{contact_phone}}': customer.contact_phone or ''
        }

        if invoice:
            replacements.update({
                '{{invoice_number}}': invoice.invoice_number or '',
                '{{invoice_amount}}': f"${invoice.total_amount or 0:,.2f}",
                '{{open_balance}}': f"${invoice.open_balance or 0:,.2f}",
                '{{due_date}}': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
                '{{days_overdue}}': str(invoice.days_overdue or 0)
            })

        result = text
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)

        return result
