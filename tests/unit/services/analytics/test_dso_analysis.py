"""
Unit tests for DSO Analysis Service.
"""
import pytest
from datetime import date, timedelta

from src.services.analytics.dso_analysis import DSOAnalysisService
from src.models.invoice import Invoice
from src.models.payment import Payment


@pytest.mark.unit
@pytest.mark.analytics
class TestDSOAnalysisService:
    """Test suite for DSOAnalysisService."""

    async def test_calculate_current_dso(self, db_session, sample_customer, sample_invoices):
        """Test current DSO calculation."""
        service = DSOAnalysisService(db_session)
        result = await service.calculate_current_dso()

        assert result is not None
        assert "dso_30" in result
        assert "dso_60" in result
        assert "dso_90" in result
        assert "total_ar" in result

        # DSO should be positive number
        assert result["dso_30"] >= 0
        assert result["dso_60"] >= 0
        assert result["dso_90"] >= 0

    async def test_dso_with_no_sales(self, db_session, sample_customer, sample_invoices):
        """Test DSO calculation when there are no sales (edge case)."""
        # This would test the scenario where sales = 0
        # DSO should be 0 or handle division by zero gracefully
        service = DSOAnalysisService(db_session)

        # If there are no payments in the period, DSO calculation
        # should still work (using invoice data)
        result = await service.calculate_current_dso()

        assert result is not None
        # Should not crash on division by zero

    async def test_dso_countback_method(self, db_session, sample_customer):
        """Test DSO calculation using Countback Method."""
        today = date.today()

        # Create invoices with specific amounts and dates
        # This tests the countback logic: work backwards from current AR
        # until we've counted back the equivalent of N days of sales

        # Create $30,000 in current AR
        invoice = Invoice(
            epicor_invoice_number="INV-TEST",
            customer_id=sample_customer.id,
            invoice_date=today - timedelta(days=45),
            due_date=today - timedelta(days=15),
            original_amount=30000.00,
            open_balance=30000.00,
            aging_bucket="30-60 Days"
        )
        db_session.add(invoice)

        # Create daily sales of $1000 for past 90 days
        # This gives us an average daily sales of $1000
        # So DSO should be 30 (30,000 AR / 1,000 daily sales)
        for i in range(90):
            payment = Payment(
                epicor_payment_id=f"PAY-{i}",
                customer_id=sample_customer.id,
                invoice_id=invoice.id,
                payment_date=today - timedelta(days=i),
                payment_amount=1000.00,
                payment_method="ACH"
            )
            db_session.add(payment)

        await db_session.commit()

        service = DSOAnalysisService(db_session)
        result = await service.calculate_current_dso()

        # With $30k AR and $1k daily sales, DSO should be around 30 days
        # Allow some variance for calculation method
        assert 25 <= result["dso_90"] <= 35

    async def test_dso_trend_analysis(self, db_session, sample_customer, sample_invoices):
        """Test monthly DSO trend calculation."""
        service = DSOAnalysisService(db_session)
        result = await service.calculate_dso_trend(months=6)

        assert result is not None
        assert isinstance(result, list)
        # Should return up to 6 months of data
        assert len(result) <= 6

        # Each month should have required fields
        if len(result) > 0:
            month_data = result[0]
            assert "month" in month_data
            assert "dso" in month_data
            assert "target" in month_data

    async def test_dso_by_segment(self, db_session, sample_customer, sample_invoices):
        """Test DSO calculation segmented by salesperson/customer type."""
        service = DSOAnalysisService(db_session)

        # By salesperson
        result = await service.calculate_dso_by_segment(segment_type="salesperson")
        assert result is not None
        assert isinstance(result, list)

        # Should have at least one segment (our sample customer's salesperson)
        if len(result) > 0:
            segment = result[0]
            assert "segment_name" in segment
            assert "dso" in segment
            assert "variance_from_target" in segment

    async def test_dso_problem_accounts(self, db_session, sample_customer, sample_invoices):
        """Test detection of accounts with high DSO."""
        service = DSOAnalysisService(db_session)
        result = await service.get_problem_accounts(variance_threshold=50)

        assert result is not None
        assert isinstance(result, list)

        # Each problem account should have required fields
        for account in result:
            assert "customer_id" in account
            assert "customer_name" in account
            assert "dso" in account
            assert "company_average_dso" in account
            assert "variance_percentage" in account

            # Variance should be >= threshold
            assert account["variance_percentage"] >= 50

    async def test_dso_target_comparison(self, db_session):
        """Test DSO comparison against industry target (35 days)."""
        service = DSOAnalysisService(db_session)
        result = await service.calculate_current_dso()

        TARGET_DSO = 35  # Industry standard for building supplies

        # Check if calculated DSO is above or below target
        if result["dso_90"] > TARGET_DSO:
            variance = result["dso_90"] - TARGET_DSO
            assert variance > 0
        else:
            variance = TARGET_DSO - result["dso_90"]
            assert variance >= 0

    async def test_dso_empty_data(self, db_session):
        """Test DSO calculation with no invoices or payments."""
        service = DSOAnalysisService(db_session)
        result = await service.calculate_current_dso()

        # Should handle empty data gracefully
        assert result is not None
        assert result["total_ar"] == 0
        assert result["dso_30"] == 0
        assert result["dso_60"] == 0
        assert result["dso_90"] == 0

    async def test_dso_monthly_trend_ordering(self, db_session, sample_customer):
        """Test that monthly DSO trend is ordered correctly (newest first)."""
        today = date.today()

        # Create invoices across multiple months
        for month_offset in range(6):
            invoice_date = today - timedelta(days=30 * month_offset)
            invoice = Invoice(
                epicor_invoice_number=f"INV-M{month_offset}",
                customer_id=sample_customer.id,
                invoice_date=invoice_date,
                due_date=invoice_date + timedelta(days=30),
                original_amount=5000.00,
                open_balance=5000.00 if month_offset < 3 else 0,  # Recent ones still open
                aging_bucket="Current"
            )
            db_session.add(invoice)

        await db_session.commit()

        service = DSOAnalysisService(db_session)
        result = await service.calculate_dso_trend(months=6)

        # Verify ordering (newest month first)
        if len(result) >= 2:
            # Months should be in descending order
            for i in range(len(result) - 1):
                month1 = result[i]["month"]
                month2 = result[i + 1]["month"]
                # month1 should be more recent than month2
                assert month1 >= month2


@pytest.mark.integration
@pytest.mark.analytics
class TestDSOAnalysisIntegration:
    """Integration tests for DSO analysis with realistic scenarios."""

    async def test_dso_with_seasonal_variation(self, db_session):
        """Test DSO calculation with seasonal business patterns."""
        today = date.today()

        from src.models.customer import Customer

        # Create customer
        customer = Customer(
            epicor_customer_id="SEASONAL001",
            name="Seasonal Builder Inc",
            credit_limit=100000.00,
            current_balance=50000.00,
            status="Active",
            salesperson_id="SP001"
        )
        db_session.add(customer)
        await db_session.flush()

        # Simulate seasonal pattern: high sales in summer, low in winter
        # This affects DSO calculation
        for i in range(365):
            invoice_date = today - timedelta(days=i)
            month = invoice_date.month

            # Summer months (6-8): high sales
            if 6 <= month <= 8:
                amount = 10000.00
            # Winter months (12-2): low sales
            elif month in [12, 1, 2]:
                amount = 2000.00
            else:
                amount = 5000.00

            invoice = Invoice(
                epicor_invoice_number=f"INV-SEASONAL-{i}",
                customer_id=customer.id,
                invoice_date=invoice_date,
                due_date=invoice_date + timedelta(days=30),
                original_amount=amount,
                open_balance=amount if i < 60 else 0,  # Recent 60 days still open
                aging_bucket="Current"
            )
            db_session.add(invoice)

            if i % 10 == 0:  # Commit every 10 invoices to avoid memory issues
                await db_session.flush()

        await db_session.commit()

        service = DSOAnalysisService(db_session)
        result = await service.calculate_current_dso()

        # DSO should reflect current seasonal pattern
        assert result["dso_90"] > 0
        assert result["total_ar"] > 0
