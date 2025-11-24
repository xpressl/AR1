"""
Unit tests for Cash Flow Forecast Service.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from src.services.analytics.cash_forecast import CashFlowForecastService
from src.models.invoice import Invoice
from src.models.note import Note


@pytest.mark.unit
@pytest.mark.analytics
class TestCashFlowForecastService:
    """Test suite for CashFlowForecastService."""

    async def test_generate_forecast_basic(self, db_session, sample_customer, sample_invoices):
        """Test basic forecast generation."""
        service = CashFlowForecastService(db_session)

        result = await service.generate_forecast(weeks=4, include_promises=False)

        assert result is not None
        assert "weekly_breakdown" in result
        assert "total_forecast" in result
        assert len(result["weekly_breakdown"]) == 4

    async def test_forecast_includes_invoice_due_dates(self, db_session, sample_customer):
        """Test that forecast includes invoices due in forecast period."""
        today = date.today()

        # Create invoice due next week
        invoice = Invoice(
            epicor_invoice_number="INV-FUTURE",
            customer_id=sample_customer.id,
            invoice_date=today,
            due_date=today + timedelta(days=7),
            original_amount=10000.00,
            open_balance=10000.00,
            aging_bucket="Current"
        )
        db_session.add(invoice)
        await db_session.commit()

        service = CashFlowForecastService(db_session)
        result = await service.generate_forecast(weeks=2, include_promises=False)

        # Should include the invoice in week 1 (days 0-6)
        week_1_forecast = result["weekly_breakdown"][0]
        assert week_1_forecast["invoice_based"] >= 10000.00

    async def test_forecast_with_promises(self, db_session, sample_customer, sample_user):
        """Test that forecast includes payment promises when enabled."""
        today = date.today()

        # Create promise to pay next week
        promise = Note(
            customer_id=sample_customer.id,
            user_id=sample_user.id,
            note_type="promise_to_pay",
            content="Customer promised to pay $5000 next week",
            promise_date=today + timedelta(days=7),
            promise_amount=5000.00,
            promise_status="pending"
        )
        db_session.add(promise)
        await db_session.commit()

        service = CashFlowForecastService(db_session)

        # With promises
        result_with = await service.generate_forecast(weeks=2, include_promises=True)
        week_1_with = result_with["weekly_breakdown"][0]

        # Without promises
        result_without = await service.generate_forecast(weeks=2, include_promises=False)
        week_1_without = result_without["weekly_breakdown"][0]

        # Promise-based forecast should be higher
        assert week_1_with["promise_based"] >= 5000.00
        assert week_1_without["promise_based"] == 0.00

    async def test_forecast_period_validation(self, db_session):
        """Test that invalid forecast periods are handled."""
        service = CashFlowForecastService(db_session)

        # Test minimum (should work)
        result = await service.generate_forecast(weeks=1)
        assert len(result["weekly_breakdown"]) == 1

        # Test maximum (should work)
        result = await service.generate_forecast(weeks=52)
        assert len(result["weekly_breakdown"]) == 52

    async def test_forecast_calculates_totals(self, db_session, sample_customer, sample_invoices):
        """Test that forecast calculates correct totals."""
        service = CashFlowForecastService(db_session)
        result = await service.generate_forecast(weeks=4, include_promises=False)

        # Total should be sum of all weekly forecasts
        expected_total = sum(
            week["invoice_based"] + week["promise_based"]
            for week in result["weekly_breakdown"]
        )

        assert abs(result["total_forecast"] - expected_total) < 0.01  # Float comparison

    async def test_forecast_empty_data(self, db_session):
        """Test forecast generation with no invoices or promises."""
        service = CashFlowForecastService(db_session)
        result = await service.generate_forecast(weeks=2)

        assert result["total_forecast"] == 0.00
        for week in result["weekly_breakdown"]:
            assert week["invoice_based"] == 0.00
            assert week["promise_based"] == 0.00

    async def test_forecast_by_customer_grouping(self, db_session, sample_customer, sample_invoices):
        """Test forecast grouped by customer."""
        service = CashFlowForecastService(db_session)
        result = await service.generate_forecast(weeks=2, group_by="customer")

        assert "by_customer" in result
        # Should have at least one customer
        assert len(result["by_customer"]) > 0

    async def test_forecast_accuracy_tracking(self, db_session, sample_customer, sample_payments):
        """Test historical forecast accuracy calculation."""
        service = CashFlowForecastService(db_session)

        # This would compare historical forecasts to actual payments
        # Simplified test - just ensure method exists and returns data
        result = await service.calculate_forecast_accuracy(months=3)

        assert result is not None
        assert "accuracy_percentage" in result or "months" in result


@pytest.mark.integration
@pytest.mark.analytics
@pytest.mark.slow
class TestCashFlowForecastIntegration:
    """Integration tests for cash flow forecasting with complex scenarios."""

    async def test_forecast_with_multiple_customers(self, db_session):
        """Test forecast with multiple customers and invoices."""
        today = date.today()

        # Create multiple customers with invoices
        customers = []
        for i in range(5):
            from src.models.customer import Customer
            customer = Customer(
                epicor_customer_id=f"CUST00{i}",
                name=f"Test Customer {i}",
                credit_limit=10000.00,
                current_balance=5000.00,
                status="Active"
            )
            db_session.add(customer)
            await db_session.flush()

            # Create invoices for each customer
            for j in range(3):
                invoice = Invoice(
                    epicor_invoice_number=f"INV-{i}-{j}",
                    customer_id=customer.id,
                    invoice_date=today - timedelta(days=30),
                    due_date=today + timedelta(days=7 * (j + 1)),
                    original_amount=2000.00,
                    open_balance=2000.00,
                    aging_bucket="Current"
                )
                db_session.add(invoice)

            customers.append(customer)

        await db_session.commit()

        service = CashFlowForecastService(db_session)
        result = await service.generate_forecast(weeks=4)

        # Should have forecasts across multiple weeks
        assert result["total_forecast"] > 0
        # With 5 customers * 3 invoices = 15 invoices of $2000 each
        assert result["total_forecast"] >= 20000.00  # At least some of them
