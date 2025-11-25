"""
Simple test to verify database setup works correctly.
"""
import pytest
from sqlalchemy import text


@pytest.mark.unit
async def test_database_tables_created(db_session):
    """Test that all tables are created in test database."""
    # Query to list all tables in SQLite
    result = await db_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    )
    tables = [row[0] for row in result.fetchall()]

    print(f"\nTables created: {tables}")

    # Verify key tables exist
    assert "customers" in tables
    assert "invoices" in tables
    assert "payments" in tables
    assert "notes" in tables
    assert "alerts" in tables
    assert "users" in tables


@pytest.mark.unit
async def test_simple_customer_insert(db_session):
    """Test that we can insert data into customer table."""
    from src.models.customer import Customer

    customer = Customer(
        epicor_customer_id="TEST001",
        name="Test Customer",
        credit_limit=10000.00,
        current_balance=0.00,
        status="Active"
    )

    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)

    assert customer.id is not None
    assert customer.name == "Test Customer"
    print(f"\nSuccessfully created customer with ID: {customer.id}")
