"""
Pytest configuration and shared fixtures for AR Control Hub tests.
"""
import pytest
import asyncio
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.db.base import Base
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.payment import Payment
from src.models.note import Note
from src.models.alert import Alert
from src.models.user import User
from src.models.task import Task


# Test database URL (use in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def sample_customer(db_session):
    """Create sample customer for testing."""
    customer = Customer(
        epicor_customer_id="CUST001",
        name="Test Building Supply Co",
        billing_email="billing@testcompany.com",
        billing_phone="555-1234",
        credit_limit=50000.00,
        current_balance=15000.00,
        status="Active",
        salesperson_id="SP001"
    )
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    return customer


@pytest.fixture
async def sample_invoices(db_session, sample_customer):
    """Create sample invoices for testing."""
    today = date.today()
    invoices = [
        Invoice(
            epicor_invoice_number="INV-001",
            customer_id=sample_customer.id,
            invoice_date=today - timedelta(days=90),
            due_date=today - timedelta(days=60),
            original_amount=5000.00,
            open_balance=5000.00,
            aging_bucket="60-90 Days"
        ),
        Invoice(
            epicor_invoice_number="INV-002",
            customer_id=sample_customer.id,
            invoice_date=today - timedelta(days=45),
            due_date=today - timedelta(days=15),
            original_amount=7500.00,
            open_balance=7500.00,
            aging_bucket="30-60 Days"
        ),
        Invoice(
            epicor_invoice_number="INV-003",
            customer_id=sample_customer.id,
            invoice_date=today - timedelta(days=10),
            due_date=today + timedelta(days=20),
            original_amount=2500.00,
            open_balance=2500.00,
            aging_bucket="Current"
        )
    ]

    for invoice in invoices:
        db_session.add(invoice)

    await db_session.commit()

    # Refresh to get IDs
    for invoice in invoices:
        await db_session.refresh(invoice)

    return invoices


@pytest.fixture
async def sample_payments(db_session, sample_customer, sample_invoices):
    """Create sample payments for testing."""
    today = date.today()
    payments = [
        Payment(
            epicor_payment_id="PAY-001",
            customer_id=sample_customer.id,
            invoice_id=sample_invoices[0].id,
            payment_date=today - timedelta(days=30),
            payment_amount=1000.00,
            payment_method="Check"
        ),
        Payment(
            epicor_payment_id="PAY-002",
            customer_id=sample_customer.id,
            invoice_id=sample_invoices[1].id,
            payment_date=today - timedelta(days=15),
            payment_amount=2500.00,
            payment_method="ACH"
        )
    ]

    for payment in payments:
        db_session.add(payment)

    await db_session.commit()

    for payment in payments:
        await db_session.refresh(payment)

    return payments


@pytest.fixture
async def sample_user(db_session):
    """Create sample user for testing."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        email="test@example.com",
        full_name="Test User",
        role="ar_specialist",
        hashed_password=pwd_context.hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_note(db_session, sample_customer, sample_user):
    """Create sample note for testing."""
    note = Note(
        customer_id=sample_customer.id,
        user_id=sample_user.id,
        note_type="phone_call",
        content="Called customer regarding overdue invoice",
        promise_status=None
    )
    db_session.add(note)
    await db_session.commit()
    await db_session.refresh(note)
    return note


@pytest.fixture
async def sample_alert(db_session, sample_customer):
    """Create sample alert for testing."""
    alert = Alert(
        customer_id=sample_customer.id,
        alert_type="inactive_account",
        severity="Critical",
        title="Account Inactive 120+ Days",
        description="No activity detected in the last 120 days",
        status="active"
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)
    return alert


@pytest.fixture
async def sample_task(db_session, sample_customer, sample_user):
    """Create sample task for testing."""
    task = Task(
        customer_id=sample_customer.id,
        assigned_to=sample_user.id,
        title="Follow up on overdue invoice",
        description="Contact customer about INV-001",
        priority="High",
        status="Open",
        due_date=date.today() + timedelta(days=7)
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
def mock_today():
    """Mock today's date for consistent testing."""
    return date(2025, 1, 15)


@pytest.fixture
def mock_datetime_now():
    """Mock current datetime for consistent testing."""
    return datetime(2025, 1, 15, 10, 30, 0)
