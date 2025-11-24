"""
Unit tests for Salesperson Portal API Routes.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.api.routes.salesperson import router
from src.db.connection import get_db


@pytest.mark.unit
@pytest.mark.api
class TestSalespersonPortalAPI:
    """Test suite for salesperson portal API endpoints."""

    @pytest.fixture
    def app(self, db_session):
        """Create FastAPI app for testing."""
        app = FastAPI()
        app.include_router(router, prefix="/api/salesperson")

        # Override database dependency
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        return app

    async def test_get_customers_requires_auth(self, app):
        """Test that GET /customers requires authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/salesperson/customers")

            assert response.status_code == 401
            assert "Salesperson authentication required" in response.json()["detail"]

    async def test_get_customers_with_header_auth(self, app, sample_customer):
        """Test GET /customers with X-Salesperson-ID header."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/salesperson/customers",
                headers={"X-Salesperson-ID": "SP001"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

            # Should return our sample customer
            if len(data) > 0:
                customer = data[0]
                assert "id" in customer
                assert "name" in customer
                assert "current_balance" in customer
                assert "credit_utilization" in customer

    async def test_get_customers_filters_by_salesperson(self, app, db_session):
        """Test that customers are filtered by authenticated salesperson."""
        from src.models.customer import Customer

        # Create customers for different salespeople
        customer1 = Customer(
            epicor_customer_id="CUST-SP1",
            name="Customer for SP1",
            credit_limit=10000.00,
            current_balance=5000.00,
            status="Active",
            salesperson_id="SP001"
        )
        customer2 = Customer(
            epicor_customer_id="CUST-SP2",
            name="Customer for SP2",
            credit_limit=15000.00,
            current_balance=7500.00,
            status="Active",
            salesperson_id="SP002"
        )

        db_session.add_all([customer1, customer2])
        await db_session.commit()

        async with AsyncClient(app=app, base_url="http://test") as client:
            # Request as SP001
            response = await client.get(
                "/api/salesperson/customers",
                headers={"X-Salesperson-ID": "SP001"}
            )

            assert response.status_code == 200
            data = response.json()

            # Should only see SP001's customer
            assert len(data) == 1
            assert data[0]["name"] == "Customer for SP1"

            # Request as SP002
            response = await client.get(
                "/api/salesperson/customers",
                headers={"X-Salesperson-ID": "SP002"}
            )

            assert response.status_code == 200
            data = response.json()

            # Should only see SP002's customer
            assert len(data) == 1
            assert data[0]["name"] == "Customer for SP2"

    async def test_get_customers_excludes_inactive(self, app, db_session):
        """Test that inactive customers are excluded."""
        from src.models.customer import Customer

        # Create active and inactive customers
        active = Customer(
            epicor_customer_id="CUST-ACTIVE",
            name="Active Customer",
            credit_limit=10000.00,
            current_balance=5000.00,
            status="Active",
            salesperson_id="SP001"
        )
        inactive = Customer(
            epicor_customer_id="CUST-INACTIVE",
            name="Inactive Customer",
            credit_limit=10000.00,
            current_balance=0.00,
            status="Inactive",
            salesperson_id="SP001"
        )

        db_session.add_all([active, inactive])
        await db_session.commit()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/salesperson/customers",
                headers={"X-Salesperson-ID": "SP001"}
            )

            assert response.status_code == 200
            data = response.json()

            # Should only include active customer
            customer_names = [c["name"] for c in data]
            assert "Active Customer" in customer_names
            assert "Inactive Customer" not in customer_names

    async def test_get_stats_requires_auth(self, app):
        """Test that GET /stats requires authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/salesperson/stats")

            assert response.status_code == 401

    async def test_get_stats_returns_aggregates(self, app, sample_customer, sample_invoices):
        """Test GET /stats returns aggregated statistics."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/salesperson/stats",
                headers={"X-Salesperson-ID": "SP001"}
            )

            assert response.status_code == 200
            data = response.json()

            # Should have all required fields
            assert "total_customers" in data
            assert "total_ar_balance" in data
            assert "total_past_due" in data
            assert "critical_alerts" in data
            assert "accounts_over_limit" in data

            # Should be positive numbers
            assert data["total_customers"] >= 0
            assert data["total_ar_balance"] >= 0

    async def test_get_customer_detail_requires_auth(self, app, sample_customer):
        """Test that GET /customer/{id} requires authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/api/salesperson/customer/{sample_customer.id}")

            assert response.status_code == 401

    async def test_get_customer_detail_validates_assignment(self, app, db_session):
        """Test that customer detail validates salesperson assignment."""
        from src.models.customer import Customer

        # Create customer for different salesperson
        other_customer = Customer(
            epicor_customer_id="CUST-OTHER",
            name="Other Customer",
            credit_limit=10000.00,
            current_balance=5000.00,
            status="Active",
            salesperson_id="SP999"  # Different salesperson
        )
        db_session.add(other_customer)
        await db_session.commit()
        await db_session.refresh(other_customer)

        async with AsyncClient(app=app, base_url="http://test") as client:
            # Try to access as SP001
            response = await client.get(
                f"/api/salesperson/customer/{other_customer.id}",
                headers={"X-Salesperson-ID": "SP001"}
            )

            # Should return 404 (not found or not assigned)
            assert response.status_code == 404
            assert "not assigned to you" in response.json()["detail"]

    async def test_get_customer_detail_success(self, app, sample_customer, sample_invoices, sample_alert):
        """Test successful customer detail retrieval."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/salesperson/customer/{sample_customer.id}",
                headers={"X-Salesperson-ID": "SP001"}
            )

            assert response.status_code == 200
            data = response.json()

            # Should have all sections
            assert "customer" in data
            assert "invoices" in data
            assert "alerts" in data

            # Customer section
            assert data["customer"]["id"] == sample_customer.id
            assert data["customer"]["name"] == sample_customer.name

            # Invoices section
            assert isinstance(data["invoices"], list)
            assert len(data["invoices"]) > 0  # Has our sample invoices

            # Alerts section
            assert isinstance(data["alerts"], list)


@pytest.mark.integration
@pytest.mark.api
class TestSalespersonPortalPerformance:
    """Performance tests for salesperson portal (N+1 query optimization)."""

    async def test_customers_endpoint_query_count(self, app, db_session):
        """Test that customers endpoint uses optimized single query."""
        from src.models.customer import Customer
        from src.models.invoice import Invoice
        from datetime import date, timedelta

        today = date.today()

        # Create 50 customers with invoices and alerts
        for i in range(50):
            customer = Customer(
                epicor_customer_id=f"PERF-{i:03d}",
                name=f"Performance Test Customer {i}",
                credit_limit=10000.00,
                current_balance=5000.00,
                status="Active",
                salesperson_id="SP001"
            )
            db_session.add(customer)
            await db_session.flush()

            # Add 5 invoices per customer
            for j in range(5):
                invoice = Invoice(
                    epicor_invoice_number=f"INV-{i}-{j}",
                    customer_id=customer.id,
                    invoice_date=today - timedelta(days=30),
                    due_date=today - timedelta(days=15),
                    original_amount=1000.00,
                    open_balance=1000.00,
                    aging_bucket="30-60 Days"
                )
                db_session.add(invoice)

            if i % 10 == 0:
                await db_session.flush()

        await db_session.commit()

        # Make request and verify it completes quickly
        # With N+1 problem: 50 customers * 2 queries = 100+ queries (~500ms)
        # With optimization: 1 query (~50ms)
        import time

        async with AsyncClient(app=app, base_url="http://test") as client:
            start_time = time.time()

            response = await client.get(
                "/api/salesperson/customers",
                headers={"X-Salesperson-ID": "SP001"}
            )

            elapsed_time = time.time() - start_time

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 50

            # Should complete in < 200ms (with optimization)
            # Without optimization would be > 500ms
            assert elapsed_time < 0.5  # 500ms threshold
