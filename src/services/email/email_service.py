"""
Email Service - W03
Handles email sending with templates and logging.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from jinja2 import Template
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from src.models.customer import Customer

logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration from environment."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("EMAIL_FROM", "ar@company.com")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "Accounts Receivable")
        self.reply_to = os.getenv("EMAIL_REPLY_TO", "")
        self.bcc = os.getenv("EMAIL_BCC", "")

        # Company info for templates
        self.company_name = os.getenv("COMPANY_NAME", "Building Supplies Co.")
        self.company_address = os.getenv("COMPANY_ADDRESS", "123 Main St, City, ST 12345")
        self.company_phone = os.getenv("COMPANY_PHONE", "(555) 123-4567")
        self.company_email = os.getenv("COMPANY_EMAIL", "ar@company.com")
        self.payment_portal_url = os.getenv("PAYMENT_PORTAL_URL", "https://pay.company.com")


class EmailService:
    """
    Service for sending AR-related emails with template support.
    """

    TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates" / "email"

    def __init__(self, db: Optional[AsyncSession] = None):
        self.config = EmailConfig()
        self.db = db

    def _load_template(self, template_name: str) -> str:
        """Load email template from file."""
        template_path = self.TEMPLATE_DIR / f"{template_name}.html"
        if template_path.exists():
            return template_path.read_text()
        raise ValueError(f"Template not found: {template_name}")

    def _render_template(self, template_content: str, context: Dict) -> str:
        """Render template with Jinja2."""
        # Add company defaults to context
        full_context = {
            "company_name": self.config.company_name,
            "company_address": self.config.company_address,
            "company_phone": self.config.company_phone,
            "company_email": self.config.company_email,
            "payment_portal_url": self.config.payment_portal_url,
            **context
        }

        template = Template(template_content)
        return template.render(**full_context)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachments: Optional[List[Dict]] = None,
        customer_id: Optional[int] = None
    ) -> Dict:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML body content
            body_text: Plain text body (optional)
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of {'filename': str, 'content': bytes, 'mime_type': str}
            customer_id: Customer ID for logging

        Returns:
            Dict with status and message_id
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = cc

            if self.config.reply_to:
                msg['Reply-To'] = self.config.reply_to

            # Add text part
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))

            # Add HTML part
            msg.attach(MIMEText(body_html, 'html'))

            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEApplication(
                        attachment['content'],
                        Name=attachment['filename']
                    )
                    part['Content-Disposition'] = f'attachment; filename="{attachment["filename"]}"'
                    msg.attach(part)

            # Build recipient list
            recipients = [to_email]
            if cc:
                recipients.extend([e.strip() for e in cc.split(',')])
            if bcc:
                recipients.extend([e.strip() for e in bcc.split(',')])
            if self.config.bcc:
                recipients.append(self.config.bcc)

            # Send email
            if self.config.smtp_host == "localhost" and self.config.smtp_port == 1025:
                # Development mode - MailHog
                with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                    server.sendmail(self.config.from_email, recipients, msg.as_string())
            else:
                # Production mode with TLS
                with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                    if self.config.smtp_use_tls:
                        server.starttls()
                    if self.config.smtp_user:
                        server.login(self.config.smtp_user, self.config.smtp_password)
                    server.sendmail(self.config.from_email, recipients, msg.as_string())

            # Log to database if available
            if self.db and customer_id:
                await self._log_email(
                    customer_id=customer_id,
                    to_email=to_email,
                    subject=subject,
                    status="sent"
                )

            logger.info(f"Email sent to {to_email}: {subject}")

            return {
                "status": "sent",
                "to": to_email,
                "subject": subject,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")

            if self.db and customer_id:
                await self._log_email(
                    customer_id=customer_id,
                    to_email=to_email,
                    subject=subject,
                    status="failed",
                    error=str(e)
                )

            return {
                "status": "failed",
                "error": str(e),
                "to": to_email
            }

    async def send_reminder(
        self,
        customer_id: int,
        reminder_type: str = "gentle",
        invoice_ids: Optional[List[int]] = None
    ) -> Dict:
        """
        Send a payment reminder email.

        Args:
            customer_id: Customer to send reminder to
            reminder_type: 'gentle' or 'firm'
            invoice_ids: Specific invoices to include (optional)

        Returns:
            Send result dict
        """
        if not self.db:
            return {"status": "error", "message": "Database connection required"}

        # Get customer
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            return {"status": "error", "message": "Customer not found"}

        if not customer.billing_email:
            return {"status": "error", "message": "Customer has no email address"}

        # Get invoices
        from src.models.invoice import Invoice
        query = select(Invoice).where(
            Invoice.customer_id == customer_id,
            Invoice.open_balance > 0
        )
        if invoice_ids:
            query = query.where(Invoice.id.in_(invoice_ids))
        query = query.order_by(Invoice.due_date.asc())

        inv_result = await self.db.execute(query)
        invoices = inv_result.scalars().all()

        # Build context
        total_due = sum(float(inv.open_balance) for inv in invoices)
        past_due = sum(float(inv.open_balance) for inv in invoices if inv.days_past_due > 0)
        max_days = max((inv.days_past_due for inv in invoices), default=0)

        context = {
            "contact_name": customer.primary_contact_name or customer.name.split()[0],
            "customer_id": customer.epicor_customer_id,
            "total_due": f"${total_due:,.2f}",
            "past_due_amount": f"${past_due:,.2f}",
            "max_days_overdue": max_days,
            "due_date": invoices[0].due_date.strftime("%B %d, %Y") if invoices else "",
            "sender_name": "AR Team",
            "invoices": [
                {
                    "invoice_number": inv.epicor_invoice_number,
                    "invoice_date": inv.invoice_date.strftime("%m/%d/%Y"),
                    "due_date": inv.due_date.strftime("%m/%d/%Y"),
                    "amount": f"${float(inv.open_balance):,.2f}",
                    "days_past_due": inv.days_past_due,
                    "is_past_due": inv.days_past_due > 0
                }
                for inv in invoices
            ]
        }

        # Load and render template
        template_name = f"reminder_{reminder_type}"
        template_content = self._load_template(template_name)
        body_html = self._render_template(template_content, context)

        # Determine subject
        if reminder_type == "gentle":
            subject = f"Friendly Reminder: Invoice Payment Due - {customer.name}"
        else:
            subject = f"URGENT: Past Due Balance Requires Immediate Attention - {customer.name}"

        return await self.send_email(
            to_email=customer.billing_email,
            subject=subject,
            body_html=body_html,
            customer_id=customer_id
        )

    async def send_statement(
        self,
        customer_id: int,
        attach_pdf: bool = True
    ) -> Dict:
        """
        Send an account statement email.

        Args:
            customer_id: Customer to send statement to
            attach_pdf: Whether to attach PDF statement

        Returns:
            Send result dict
        """
        if not self.db:
            return {"status": "error", "message": "Database connection required"}

        # Get customer with invoices
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            return {"status": "error", "message": "Customer not found"}

        if not customer.billing_email:
            return {"status": "error", "message": "Customer has no email address"}

        # Get invoices
        from src.models.invoice import Invoice
        inv_result = await self.db.execute(
            select(Invoice)
            .where(Invoice.customer_id == customer_id)
            .where(Invoice.open_balance != 0)
            .order_by(Invoice.due_date.asc())
        )
        invoices = inv_result.scalars().all()

        # Calculate aging
        aging = {"current": 0, "1-30": 0, "31-60": 0, "61-90": 0, "90+": 0}
        for inv in invoices:
            bucket = inv.aging_bucket
            aging[bucket] = aging.get(bucket, 0) + float(inv.open_balance)

        total = sum(aging.values())

        # Build context
        context = {
            "statement_date": datetime.now().strftime("%B %d, %Y"),
            "customer_id": customer.epicor_customer_id,
            "customer_name": customer.name,
            "customer_contact": customer.primary_contact_name,
            "customer_address_line1": customer.billing_address_line1 or "",
            "customer_address_line2": customer.billing_address_line2 or "",
            "customer_city": customer.billing_city or "",
            "customer_state": customer.billing_state or "",
            "customer_zip": customer.billing_zip or "",
            "credit_limit": f"${float(customer.credit_limit or 0):,.2f}",
            "terms_code": customer.terms_code or "Net 30",
            "last_payment_date": customer.last_payment_date.strftime("%m/%d/%Y") if customer.last_payment_date else "N/A",
            "last_payment_amount": "$0.00",  # TODO: Get from payments
            "aging_current": f"${aging['current']:,.2f}",
            "aging_1_30": f"${aging['1-30']:,.2f}",
            "aging_31_60": f"${aging['31-60']:,.2f}",
            "aging_61_plus": f"${aging['61-90'] + aging['90+']:,.2f}",
            "aging_current_pct": round(aging['current'] / total * 100) if total > 0 else 0,
            "aging_1_30_pct": round(aging['1-30'] / total * 100) if total > 0 else 0,
            "aging_31_60_pct": round(aging['31-60'] / total * 100) if total > 0 else 0,
            "aging_61_90_pct": round(aging['61-90'] / total * 100) if total > 0 else 0,
            "aging_90_plus_pct": round(aging['90+'] / total * 100) if total > 0 else 0,
            "total_balance": f"${total:,.2f}",
            "past_due_amount": f"${sum(float(inv.open_balance) for inv in invoices if inv.days_past_due > 0):,.2f}",
            "invoices": [
                {
                    "invoice_number": inv.epicor_invoice_number,
                    "invoice_date": inv.invoice_date.strftime("%m/%d/%Y"),
                    "due_date": inv.due_date.strftime("%m/%d/%Y"),
                    "po_number": inv.po_number or "",
                    "description": inv.invoice_type,
                    "original_amount": f"${float(inv.original_amount):,.2f}",
                    "open_balance": f"${float(inv.open_balance):,.2f}",
                    "is_past_due": inv.days_past_due > 0,
                    "is_credit": float(inv.open_balance) < 0
                }
                for inv in invoices
            ]
        }

        template_content = self._load_template("statement")
        body_html = self._render_template(template_content, context)

        attachments = []
        # TODO: Generate PDF statement if attach_pdf is True

        return await self.send_email(
            to_email=customer.billing_email,
            subject=f"Account Statement - {customer.name} - {context['statement_date']}",
            body_html=body_html,
            attachments=attachments if attachments else None,
            customer_id=customer_id
        )

    async def _log_email(
        self,
        customer_id: int,
        to_email: str,
        subject: str,
        status: str,
        email_type: str = "custom",
        error: Optional[str] = None
    ) -> None:
        """Log email to database."""
        from src.models.email_log import EmailLog

        log = EmailLog(
            customer_id=customer_id,
            recipient_email=to_email,
            subject=subject,
            email_type=email_type,
            delivery_status=status,
            sent_at=datetime.utcnow() if status == "sent" else None
        )
        self.db.add(log)
        await self.db.commit()
