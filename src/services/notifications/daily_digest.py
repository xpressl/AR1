"""
Daily Email Digest Service - Phase 2
Sends daily AR summary emails to AR team members.
"""
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from jinja2 import Template
import logging

from src.db.connection import async_session
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.alert import Alert
from src.models.note import Note
from src.models.user import User
from src.services.email.email_service import EmailService

logger = logging.getLogger(__name__)


class DailyDigestService:
    """
    Generates and sends daily AR digest emails.
    Sent at 6:30 AM to AR Manager and AR Specialists.
    """

    DIGEST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; }
        .header { background: #1f2937; color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .header h1 { margin: 0; font-size: 24px; }
        .header .date { opacity: 0.8; font-size: 14px; }
        .section { padding: 20px; border: 1px solid #e5e7eb; border-top: none; }
        .section-title { font-size: 16px; font-weight: bold; color: #1f2937; margin-bottom: 15px; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; }
        .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
        .stat-box { background: #f9fafb; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-box .label { font-size: 12px; color: #6b7280; text-transform: uppercase; }
        .stat-box .value { font-size: 24px; font-weight: bold; color: #1f2937; }
        .stat-box.alert { background: #fef2f2; }
        .stat-box.alert .value { color: #dc2626; }
        .alert-list { margin: 0; padding: 0; list-style: none; }
        .alert-item { padding: 10px; background: #fef2f2; border-left: 4px solid #dc2626; margin-bottom: 8px; border-radius: 0 4px 4px 0; }
        .alert-item.high { border-color: #f97316; background: #fff7ed; }
        .account-list { margin: 0; padding: 0; list-style: none; }
        .account-item { padding: 12px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; }
        .account-item:last-child { border-bottom: none; }
        .promise-list { margin: 0; padding: 0; list-style: none; }
        .promise-item { padding: 10px; background: #fef3c7; border-left: 4px solid #f59e0b; margin-bottom: 8px; border-radius: 0 4px 4px 0; }
        .btn { display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; }
        .footer { padding: 20px; background: #f9fafb; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; color: #6b7280; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AR Daily Digest</h1>
        <div class="date">{{ digest_date }}</div>
    </div>

    <div class="section">
        <div class="section-title">Key Metrics</div>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="label">Total AR</div>
                <div class="value">${{ total_ar | format_number }}</div>
            </div>
            <div class="stat-box">
                <div class="label">Past Due</div>
                <div class="value">${{ past_due | format_number }}</div>
            </div>
            <div class="stat-box">
                <div class="label">DSO</div>
                <div class="value">{{ dso }} days</div>
            </div>
            <div class="stat-box {% if critical_alerts > 0 %}alert{% endif %}">
                <div class="label">Critical Alerts</div>
                <div class="value">{{ critical_alerts }}</div>
            </div>
            <div class="stat-box">
                <div class="label">New Alerts</div>
                <div class="value">{{ new_alerts }}</div>
            </div>
            <div class="stat-box">
                <div class="label">Promises Due</div>
                <div class="value">{{ promises_due_today }}</div>
            </div>
        </div>
    </div>

    {% if critical_alert_list %}
    <div class="section">
        <div class="section-title">Critical Alerts Requiring Action</div>
        <ul class="alert-list">
            {% for alert in critical_alert_list %}
            <li class="alert-item">
                <strong>{{ alert.customer_name }}</strong>: {{ alert.title }}<br>
                <small>{{ alert.description }}</small>
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    {% if top_priority_accounts %}
    <div class="section">
        <div class="section-title">Top Priority Accounts</div>
        <ul class="account-list">
            {% for account in top_priority_accounts %}
            <li class="account-item">
                <div>
                    <strong>{{ account.name }}</strong><br>
                    <small>{{ account.reason }}</small>
                </div>
                <div style="text-align: right;">
                    <strong>${{ account.past_due | format_number }}</strong><br>
                    <small>{{ account.days_overdue }} days overdue</small>
                </div>
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    {% if promises_due %}
    <div class="section">
        <div class="section-title">Promises Due Today</div>
        <ul class="promise-list">
            {% for promise in promises_due %}
            <li class="promise-item">
                <strong>{{ promise.customer_name }}</strong>: ${{ promise.amount | format_number }} promised
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    {% if import_status %}
    <div class="section">
        <div class="section-title">Data Import Status</div>
        <p>
            Last import: {{ import_status.last_run }}<br>
            Status: <strong>{{ import_status.status }}</strong><br>
            Records processed: {{ import_status.records_processed }}
        </p>
    </div>
    {% endif %}

    <div class="section" style="text-align: center;">
        <a href="{{ app_url }}" class="btn">Open AR Control Hub</a>
    </div>

    <div class="footer">
        <p>This is an automated daily digest from AR Control Hub.</p>
        <p>{{ company_name }} | Generated at {{ generated_at }}</p>
    </div>
</body>
</html>
"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_service = EmailService(db)

    async def generate_digest_data(self) -> Dict:
        """Gather all data needed for the daily digest."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Key Metrics
        metrics = await self._get_key_metrics()

        # Critical Alerts
        critical_alerts = await self._get_critical_alerts()

        # Top Priority Accounts
        top_accounts = await self._get_top_priority_accounts()

        # Promises Due Today
        promises_due = await self._get_promises_due_today()

        # Import Status
        import_status = await self._get_import_status()

        return {
            "digest_date": today.strftime("%A, %B %d, %Y"),
            "total_ar": metrics["total_ar"],
            "past_due": metrics["past_due"],
            "dso": metrics["dso"],
            "critical_alerts": metrics["critical_alert_count"],
            "new_alerts": metrics["new_alert_count"],
            "promises_due_today": len(promises_due),
            "critical_alert_list": critical_alerts[:5],  # Top 5
            "top_priority_accounts": top_accounts[:10],  # Top 10
            "promises_due": promises_due,
            "import_status": import_status,
            "app_url": os.getenv("APP_URL", "http://localhost:3000"),
            "company_name": os.getenv("COMPANY_NAME", "Building Supplies Co."),
            "generated_at": datetime.now().strftime("%I:%M %p")
        }

    async def _get_key_metrics(self) -> Dict:
        """Get key AR metrics."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Total AR
        ar_result = await self.db.execute(
            select(func.sum(Invoice.open_balance)).where(Invoice.open_balance > 0)
        )
        total_ar = float(ar_result.scalar() or 0)

        # Past Due
        past_due_result = await self.db.execute(
            select(func.sum(Invoice.open_balance)).where(
                Invoice.open_balance > 0,
                Invoice.due_date < today
            )
        )
        past_due = float(past_due_result.scalar() or 0)

        # DSO (simplified calculation)
        dso = round((total_ar / (total_ar / 30)) if total_ar > 0 else 0)

        # Critical Alerts
        critical_result = await self.db.execute(
            select(func.count(Alert.id)).where(
                Alert.severity == 'Critical',
                Alert.status == 'active'
            )
        )
        critical_count = critical_result.scalar() or 0

        # New Alerts (last 24 hours)
        new_result = await self.db.execute(
            select(func.count(Alert.id)).where(
                Alert.created_at >= yesterday
            )
        )
        new_count = new_result.scalar() or 0

        return {
            "total_ar": total_ar,
            "past_due": past_due,
            "dso": dso,
            "critical_alert_count": critical_count,
            "new_alert_count": new_count
        }

    async def _get_critical_alerts(self) -> List[Dict]:
        """Get critical alerts with customer info."""
        result = await self.db.execute(
            select(Alert, Customer.name)
            .join(Customer, Alert.customer_id == Customer.id)
            .where(Alert.severity == 'Critical', Alert.status == 'active')
            .order_by(Alert.created_at.desc())
            .limit(10)
        )
        rows = result.all()

        return [
            {
                "customer_name": row[1],
                "title": row[0].title,
                "description": row[0].description
            }
            for row in rows
        ]

    async def _get_top_priority_accounts(self) -> List[Dict]:
        """Get accounts requiring immediate attention."""
        today = date.today()

        # Get customers with highest past due
        result = await self.db.execute(
            select(
                Customer.id,
                Customer.name,
                func.sum(Invoice.open_balance).label('past_due'),
                func.max(func.extract('day', func.current_date() - Invoice.due_date)).label('max_days')
            )
            .join(Invoice, Customer.id == Invoice.customer_id)
            .where(
                Invoice.open_balance > 0,
                Invoice.due_date < today
            )
            .group_by(Customer.id, Customer.name)
            .order_by(func.sum(Invoice.open_balance).desc())
            .limit(10)
        )
        rows = result.all()

        return [
            {
                "name": row[1],
                "past_due": float(row[2] or 0),
                "days_overdue": int(row[3] or 0),
                "reason": f"${float(row[2] or 0):,.0f} past due, {int(row[3] or 0)}+ days"
            }
            for row in rows
        ]

    async def _get_promises_due_today(self) -> List[Dict]:
        """Get promises due today."""
        today = date.today()

        result = await self.db.execute(
            select(Note, Customer.name)
            .join(Customer, Note.customer_id == Customer.id)
            .where(
                Note.note_type == 'promise_to_pay',
                Note.promise_status == 'pending',
                Note.promise_date == today
            )
        )
        rows = result.all()

        return [
            {
                "customer_name": row[1],
                "amount": float(row[0].promise_amount or 0)
            }
            for row in rows
        ]

    async def _get_import_status(self) -> Optional[Dict]:
        """Get last import run status."""
        from src.models.import_run import ImportRun

        result = await self.db.execute(
            select(ImportRun)
            .order_by(ImportRun.started_at.desc())
            .limit(1)
        )
        run = result.scalar_one_or_none()

        if not run:
            return None

        return {
            "last_run": run.started_at.strftime("%Y-%m-%d %I:%M %p") if run.started_at else "N/A",
            "status": run.status,
            "records_processed": (
                (run.customers_imported or 0) +
                (run.invoices_imported or 0) +
                (run.payments_imported or 0)
            )
        }

    def render_digest(self, data: Dict) -> str:
        """Render the digest HTML."""
        # Add format_number filter
        def format_number(value):
            return f"{value:,.2f}" if value else "0.00"

        template = Template(self.DIGEST_TEMPLATE)
        template.environment.filters['format_number'] = format_number

        return template.render(**data)

    async def send_digest(self, recipients: List[str]) -> Dict:
        """Generate and send daily digest to recipients."""
        logger.info(f"Generating daily digest for {len(recipients)} recipients")

        try:
            # Generate data
            data = await self.generate_digest_data()

            # Render HTML
            html_content = self.render_digest(data)

            # Send to each recipient
            results = []
            for email in recipients:
                result = await self.email_service.send_email(
                    to_email=email,
                    subject=f"AR Daily Digest - {data['digest_date']}",
                    body_html=html_content
                )
                results.append({"email": email, "status": result["status"]})

            success_count = sum(1 for r in results if r["status"] == "sent")

            return {
                "status": "success" if success_count == len(recipients) else "partial",
                "sent": success_count,
                "failed": len(recipients) - success_count,
                "results": results
            }

        except Exception as e:
            logger.error(f"Failed to send daily digest: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }


async def send_daily_digest():
    """
    Standalone function to send daily digest.
    Called by scheduler at 6:30 AM.
    """
    async with async_session() as session:
        service = DailyDigestService(session)

        # Get AR team users
        result = await session.execute(
            select(User.email).where(
                User.role.in_(['ar_manager', 'ar_specialist']),
                User.is_active == True
            )
        )
        recipients = [row[0] for row in result.all() if row[0]]

        if not recipients:
            logger.warning("No recipients found for daily digest")
            return {"status": "skipped", "reason": "No recipients"}

        return await service.send_digest(recipients)
