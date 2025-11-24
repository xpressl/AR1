"""
Alert Rules Engine - A01
Core engine that runs all alert detection rules and manages alert lifecycle.
"""
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.alert import Alert, AlertType, AlertSeverity
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.note import Note
from src.models.payment import Payment

logger = logging.getLogger(__name__)


class AlertRulesEngine:
    """
    Main alert rules engine that coordinates all alert detection.
    Run after each data import to generate and resolve alerts.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.alerts_created = 0
        self.alerts_resolved = 0

    async def run_all_rules(self) -> dict:
        """
        Run all alert detection rules.
        Returns summary of alerts created and resolved.
        """
        logger.info("Starting alert rules engine...")

        # Run each detector
        await self._detect_inactive_accounts()
        await self._detect_credit_limit_issues()
        await self._detect_overdue_invoices()
        await self._detect_broken_promises()
        await self._detect_unapplied_credits()

        # Auto-resolve alerts that no longer apply
        await self._auto_resolve_alerts()

        await self.db.commit()

        summary = {
            "alerts_created": self.alerts_created,
            "alerts_resolved": self.alerts_resolved,
            "run_at": datetime.now().isoformat()
        }

        logger.info(f"Alert rules completed: {summary}")
        return summary

    async def _detect_inactive_accounts(self):
        """
        Detect customers with no purchases in 90+ days but still have balance.
        Alert type: inactive_but_owing
        """
        logger.info("Detecting inactive accounts...")

        result = await self.db.execute(
            select(Customer)
            .where(Customer.current_balance > 100)  # Threshold
            .where(Customer.status == "Active")
        )
        customers = result.scalars().all()

        for customer in customers:
            if not customer.is_inactive:
                continue

            days = customer.days_since_last_invoice or 0

            # Determine severity
            if days > 180:
                severity = AlertSeverity.CRITICAL.value
            elif days > 120:
                severity = AlertSeverity.HIGH.value
            else:
                severity = AlertSeverity.MEDIUM.value

            # Check if alert already exists
            existing = await self._get_active_alert(
                customer.id,
                AlertType.INACTIVE_BUT_OWING.value
            )

            if existing:
                # Update severity if changed
                if existing.severity != severity:
                    existing.severity = severity
            else:
                # Create new alert
                alert = Alert(
                    customer_id=customer.id,
                    alert_type=AlertType.INACTIVE_BUT_OWING.value,
                    severity=severity,
                    message=f"No purchases in {days} days with ${float(customer.current_balance):.2f} balance",
                    is_active=True
                )
                self.db.add(alert)
                self.alerts_created += 1

    async def _detect_credit_limit_issues(self):
        """
        Detect customers near or over credit limit.
        Alert types: near_credit_limit, over_credit_limit
        """
        logger.info("Detecting credit limit issues...")

        result = await self.db.execute(
            select(Customer)
            .where(Customer.credit_limit > 0)
            .where(Customer.current_balance > 0)
        )
        customers = result.scalars().all()

        for customer in customers:
            utilization = customer.credit_utilization

            if customer.is_over_credit_limit:
                # Over limit - Critical
                existing = await self._get_active_alert(
                    customer.id,
                    AlertType.OVER_CREDIT_LIMIT.value
                )
                if not existing:
                    over_by = float(customer.current_balance - customer.credit_limit)
                    alert = Alert(
                        customer_id=customer.id,
                        alert_type=AlertType.OVER_CREDIT_LIMIT.value,
                        severity=AlertSeverity.CRITICAL.value,
                        message=f"Over credit limit by ${over_by:.2f} ({utilization:.1f}% utilization)",
                        is_active=True
                    )
                    self.db.add(alert)
                    self.alerts_created += 1

            elif customer.is_near_credit_limit:
                # Near limit (80%+) - Medium
                existing = await self._get_active_alert(
                    customer.id,
                    AlertType.NEAR_CREDIT_LIMIT.value
                )
                if not existing:
                    alert = Alert(
                        customer_id=customer.id,
                        alert_type=AlertType.NEAR_CREDIT_LIMIT.value,
                        severity=AlertSeverity.MEDIUM.value,
                        message=f"At {utilization:.1f}% of credit limit",
                        is_active=True
                    )
                    self.db.add(alert)
                    self.alerts_created += 1

    async def _detect_overdue_invoices(self):
        """
        Detect invoices 60+ and 90+ days past due.
        Alert types: long_overdue_60, long_overdue_90
        """
        logger.info("Detecting overdue invoices...")

        result = await self.db.execute(
            select(Invoice)
            .where(Invoice.open_balance > 0)
            .where(Invoice.status == "Open")
        )
        invoices = result.scalars().all()

        for invoice in invoices:
            days = invoice.days_past_due

            if days >= 90:
                # 90+ days - Critical
                existing = await self._get_active_alert(
                    invoice.customer_id,
                    AlertType.LONG_OVERDUE_90.value,
                    invoice.id
                )
                if not existing:
                    alert = Alert(
                        customer_id=invoice.customer_id,
                        invoice_id=invoice.id,
                        alert_type=AlertType.LONG_OVERDUE_90.value,
                        severity=AlertSeverity.CRITICAL.value,
                        message=f"Invoice {invoice.epicor_invoice_number} is {days} days past due (${float(invoice.open_balance):.2f})",
                        is_active=True
                    )
                    self.db.add(alert)
                    self.alerts_created += 1

            elif days >= 60:
                # 60-89 days - High
                existing = await self._get_active_alert(
                    invoice.customer_id,
                    AlertType.LONG_OVERDUE_60.value,
                    invoice.id
                )
                if not existing:
                    alert = Alert(
                        customer_id=invoice.customer_id,
                        invoice_id=invoice.id,
                        alert_type=AlertType.LONG_OVERDUE_60.value,
                        severity=AlertSeverity.HIGH.value,
                        message=f"Invoice {invoice.epicor_invoice_number} is {days} days past due (${float(invoice.open_balance):.2f})",
                        is_active=True
                    )
                    self.db.add(alert)
                    self.alerts_created += 1

    async def _detect_broken_promises(self):
        """
        Detect promise-to-pay notes where date has passed.
        Alert type: broken_promise
        """
        logger.info("Detecting broken promises...")

        result = await self.db.execute(
            select(Note)
            .where(Note.note_type == "promise_to_pay")
            .where(Note.promise_status == "pending")
        )
        promises = result.scalars().all()

        for promise in promises:
            if not promise.is_promise_due:
                continue

            # Mark promise as broken
            promise.promise_status = "broken"

            # Create alert
            existing = await self._get_active_alert(
                promise.customer_id,
                AlertType.BROKEN_PROMISE.value
            )
            if not existing:
                alert = Alert(
                    customer_id=promise.customer_id,
                    alert_type=AlertType.BROKEN_PROMISE.value,
                    severity=AlertSeverity.CRITICAL.value,
                    message=f"Promise to pay ${float(promise.promise_amount):.2f} by {promise.promise_date} was not kept",
                    is_active=True
                )
                self.db.add(alert)
                self.alerts_created += 1

    async def _detect_unapplied_credits(self):
        """
        Detect customers with significant unapplied payments or credits.
        Alert type: unapplied_credits
        """
        logger.info("Detecting unapplied credits...")

        result = await self.db.execute(
            select(Payment)
            .where(Payment.unapplied_amount > 500)  # Threshold
        )
        payments = result.scalars().all()

        # Group by customer
        customer_unapplied = {}
        for p in payments:
            if p.customer_id not in customer_unapplied:
                customer_unapplied[p.customer_id] = 0
            customer_unapplied[p.customer_id] += float(p.unapplied_amount or 0)

        for customer_id, total_unapplied in customer_unapplied.items():
            existing = await self._get_active_alert(
                customer_id,
                AlertType.UNAPPLIED_CREDITS.value
            )
            if not existing:
                alert = Alert(
                    customer_id=customer_id,
                    alert_type=AlertType.UNAPPLIED_CREDITS.value,
                    severity=AlertSeverity.LOW.value,
                    message=f"${total_unapplied:.2f} in unapplied payments needs to be applied or refunded",
                    is_active=True
                )
                self.db.add(alert)
                self.alerts_created += 1

    async def _auto_resolve_alerts(self):
        """
        Auto-resolve alerts that no longer apply.
        """
        logger.info("Auto-resolving alerts...")

        # Get all active alerts
        result = await self.db.execute(
            select(Alert).where(Alert.is_active == True)
        )
        alerts = result.scalars().all()

        for alert in alerts:
            should_resolve = False

            if alert.alert_type == AlertType.INACTIVE_BUT_OWING.value:
                # Check if customer is now active or balance is zero
                cust_result = await self.db.execute(
                    select(Customer).where(Customer.id == alert.customer_id)
                )
                customer = cust_result.scalar_one_or_none()
                if customer and (not customer.is_inactive or customer.current_balance <= 0):
                    should_resolve = True

            elif alert.alert_type == AlertType.OVER_CREDIT_LIMIT.value:
                cust_result = await self.db.execute(
                    select(Customer).where(Customer.id == alert.customer_id)
                )
                customer = cust_result.scalar_one_or_none()
                if customer and not customer.is_over_credit_limit:
                    should_resolve = True

            elif alert.alert_type in [AlertType.LONG_OVERDUE_60.value, AlertType.LONG_OVERDUE_90.value]:
                if alert.invoice_id:
                    inv_result = await self.db.execute(
                        select(Invoice).where(Invoice.id == alert.invoice_id)
                    )
                    invoice = inv_result.scalar_one_or_none()
                    if invoice and invoice.open_balance <= 0:
                        should_resolve = True

            if should_resolve:
                alert.is_active = False
                alert.resolved_at = datetime.now()
                alert.resolution_note = "Auto-resolved: condition no longer applies"
                self.alerts_resolved += 1

    async def _get_active_alert(
        self,
        customer_id: int,
        alert_type: str,
        invoice_id: Optional[int] = None
    ) -> Optional[Alert]:
        """Check if an active alert already exists"""
        conditions = [
            Alert.customer_id == customer_id,
            Alert.alert_type == alert_type,
            Alert.is_active == True
        ]
        if invoice_id:
            conditions.append(Alert.invoice_id == invoice_id)

        result = await self.db.execute(
            select(Alert).where(and_(*conditions))
        )
        return result.scalar_one_or_none()
