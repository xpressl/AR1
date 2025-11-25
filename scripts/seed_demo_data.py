"""
Seed Demo Data for AR Control Hub

Creates realistic sample data for demonstrations and user acceptance testing.

Usage:
    python scripts/seed_demo_data.py --scenario demo
    python scripts/seed_demo_data.py --scenario uat
    python scripts/seed_demo_data.py --scenario performance  # 1000+ customers
"""
import asyncio
import argparse
from datetime import date, timedelta, datetime
from decimal import Decimal
import random
from faker import Faker

from src.db.connection import async_session
from src.models import (
    Customer, Invoice, Payment, Note, Alert, Task, User
)

fake = Faker()
Faker.seed(42)  # Reproducible data
random.seed(42)


class DemoDataSeeder:
    """Seeds database with realistic demo data."""

    def __init__(self, scenario="demo"):
        self.scenario = scenario
        self.today = date.today()
        self.users = []
        self.customers = []
        self.invoices = []
        self.payments = []

    async def seed(self):
        """Main seeding method."""
        print(f"🌱 Seeding {self.scenario} data...")

        async with async_session() as session:
            # Create users first
            await self._create_users(session)
            await session.commit()
            print(f"✅ Created {len(self.users)} users")

            # Create customers
            await self._create_customers(session)
            await session.commit()
            print(f"✅ Created {len(self.customers)} customers")

            # Create invoices
            await self._create_invoices(session)
            await session.commit()
            print(f"✅ Created {len(self.invoices)} invoices")

            # Create payments
            await self._create_payments(session)
            await session.commit()
            print(f"✅ Created {len(self.payments)} payments")

            # Create notes
            notes_count = await self._create_notes(session)
            await session.commit()
            print(f"✅ Created {notes_count} notes")

            # Create tasks
            tasks_count = await self._create_tasks(session)
            await session.commit()
            print(f"✅ Created {tasks_count} tasks")

            # Generate alerts
            alerts_count = await self._create_alerts(session)
            await session.commit()
            print(f"✅ Created {alerts_count} alerts")

        print(f"\n🎉 Demo data seeded successfully!")
        self._print_summary()

    async def _create_users(self, session):
        """Create demo users."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        users_data = [
            {
                "email": "sarah.martinez@company.com",
                "full_name": "Sarah Martinez",
                "role": "ar_specialist",
                "password": "demo123"
            },
            {
                "email": "michael.chen@company.com",
                "full_name": "Michael Chen",
                "role": "ar_manager",
                "password": "demo123"
            },
            {
                "email": "admin@company.com",
                "full_name": "Admin User",
                "role": "ar_manager",
                "password": "demo123"
            }
        ]

        for user_data in users_data:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                hashed_password=pwd_context.hash(user_data["password"]),
                is_active=True
            )
            session.add(user)
            self.users.append(user)

        await session.flush()

    async def _create_customers(self, session):
        """Create demo customers with realistic distribution."""
        # Determine number of customers based on scenario
        if self.scenario == "demo":
            num_customers = 50
        elif self.scenario == "uat":
            num_customers = 100
        else:  # performance
            num_customers = 1000

        # Salesperson assignments
        salespeople = ["SP001", "SP002", "SP003", "SP004", "SP005"]

        # Create customers with realistic distribution
        for i in range(num_customers):
            # Customer status distribution
            status = self._get_customer_status(i, num_customers)

            # Credit limit ranges
            credit_limit = random.choice([
                10000, 15000, 20000, 25000, 30000,
                40000, 50000, 75000, 100000, 150000
            ])

            # Current balance (realistic relationship to credit limit)
            if status == "Active":
                balance_pct = random.uniform(0.2, 0.95)
            else:
                balance_pct = random.uniform(0, 0.3)

            current_balance = round(credit_limit * balance_pct, 2)

            customer = Customer(
                epicor_customer_id=f"CUST{i+1:04d}",
                name=self._generate_customer_name(),
                billing_email=fake.company_email(),
                billing_phone=fake.phone_number()[:20],
                billing_address_line1=fake.street_address()[:255],
                billing_city=fake.city()[:100],
                billing_state=fake.state_abbr(),
                billing_zip=fake.zipcode()[:10],
                credit_limit=Decimal(str(credit_limit)),
                current_balance=Decimal(str(current_balance)),
                status=status,
                salesperson_id=random.choice(salespeople),
                customer_type=random.choice(["Contractor", "Builder", "Retailer", "Government"]),
                terms_code=random.choice(["Net 30", "Net 45", "Net 60", "2/10 Net 30"]),
                last_invoice_date=self.today - timedelta(days=random.randint(1, 90)),
                last_payment_date=self.today - timedelta(days=random.randint(1, 60))
            )

            session.add(customer)
            self.customers.append(customer)

        await session.flush()

    def _get_customer_status(self, index, total):
        """Get customer status based on realistic distribution."""
        pct = (index / total) * 100

        if pct < 10:  # 10% inactive/on hold
            return random.choice(["Inactive", "Credit Hold"])
        else:
            return "Active"

    def _generate_customer_name(self):
        """Generate realistic building supply customer names."""
        prefixes = ["", "ABC", "Best", "Pro", "Superior", "Quality", "Premier", "Elite"]
        middle = [
            "Building", "Construction", "Lumber", "Supply", "Materials",
            "Contractors", "Builders", "Home", "Hardware"
        ]
        suffixes = ["Co", "Inc", "LLC", "Supply", "Center", "Depot", "Warehouse", "Group"]

        prefix = random.choice(prefixes)
        mid = random.choice(middle)
        suffix = random.choice(suffixes)

        if prefix:
            return f"{prefix} {mid} {suffix}"
        else:
            return f"{fake.city()} {mid} {suffix}"

    async def _create_invoices(self, session):
        """Create invoices with realistic aging distribution."""
        # Determine invoice count
        if self.scenario == "demo":
            invoices_per_customer = 4
        elif self.scenario == "uat":
            invoices_per_customer = 6
        else:
            invoices_per_customer = 10

        invoice_num = 1

        for customer in self.customers:
            if customer.status != "Active":
                # Inactive customers have fewer/no open invoices
                invoices_per_customer = random.randint(0, 2)

            for _ in range(invoices_per_customer):
                # Aging distribution (weighted toward current/recent)
                aging_days = self._get_invoice_aging_days()

                invoice_date = self.today - timedelta(days=aging_days + 30)
                due_date = invoice_date + timedelta(days=30)  # Net 30 terms

                # Invoice amounts realistic for building supplies
                original_amount = round(random.uniform(500, 15000), 2)

                # Some invoices partially paid
                if random.random() < 0.3:  # 30% partially paid
                    open_balance = round(original_amount * random.uniform(0.3, 0.9), 2)
                else:
                    open_balance = original_amount

                # Determine aging bucket
                days_past_due = max(0, (self.today - due_date).days)
                aging_bucket = self._get_aging_bucket(days_past_due)

                invoice = Invoice(
                    epicor_invoice_number=f"INV-{invoice_num:06d}",
                    customer_id=customer.id,
                    invoice_date=invoice_date,
                    due_date=due_date,
                    original_amount=Decimal(str(original_amount)),
                    open_balance=Decimal(str(open_balance)),
                    aging_bucket=aging_bucket,
                    po_number=f"PO-{random.randint(1000, 9999)}" if random.random() < 0.7 else None
                )

                session.add(invoice)
                self.invoices.append(invoice)
                invoice_num += 1

        await session.flush()

    def _get_invoice_aging_days(self):
        """Get realistic invoice aging days with weighted distribution."""
        weights = [
            (0, 30, 0.4),    # 40% current
            (31, 60, 0.25),  # 25% 1-30 days past due
            (61, 90, 0.20),  # 20% 31-60 days
            (91, 120, 0.10), # 10% 61-90 days
            (121, 180, 0.05) # 5% 90+ days
        ]

        rand = random.random()
        cumulative = 0

        for min_days, max_days, weight in weights:
            cumulative += weight
            if rand <= cumulative:
                return random.randint(min_days, max_days)

        return random.randint(0, 30)  # Default to current

    def _get_aging_bucket(self, days_past_due):
        """Get aging bucket label."""
        if days_past_due <= 0:
            return "Current"
        elif days_past_due <= 30:
            return "1-30 Days"
        elif days_past_due <= 60:
            return "31-60 Days"
        elif days_past_due <= 90:
            return "61-90 Days"
        else:
            return "90+ Days"

    async def _create_payments(self, session):
        """Create realistic payment history."""
        payment_num = 1

        # Create payments for some invoices
        for invoice in self.invoices:
            # Skip if fully paid
            if invoice.open_balance >= invoice.original_amount:
                continue

            # Amount paid is difference
            amount_paid = float(invoice.original_amount - invoice.open_balance)

            payment = Payment(
                epicor_payment_id=f"PMT-{payment_num:06d}",
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                payment_date=invoice.due_date + timedelta(days=random.randint(-10, 45)),
                payment_amount=Decimal(str(amount_paid)),
                payment_method=random.choice(["Check", "ACH", "Wire", "Credit Card"])
            )

            session.add(payment)
            self.payments.append(payment)
            payment_num += 1

        await session.flush()

    async def _create_notes(self, session):
        """Create notes documenting customer interactions."""
        count = 0

        # Select customers for notes (30% of customers)
        customers_with_notes = random.sample(
            self.customers,
            k=int(len(self.customers) * 0.3)
        )

        note_types = [
            ("phone_call", "Called customer to discuss overdue invoice. Customer indicated cash flow issues but will pay within 2 weeks."),
            ("phone_call", "Left voicemail requesting callback regarding past due balance."),
            ("email_sent", "Sent statement of account showing aging detail."),
            ("email_sent", "Sent payment reminder for invoices past 60 days."),
            ("promise_to_pay", "Customer promises to pay $5,000 by Friday."),
            ("promise_to_pay", "Spoke with accounts payable - will mail check tomorrow for full balance."),
            ("general", "Customer disputed invoice INV-00123. Researching with operations."),
            ("general", "Applied partial payment to oldest invoices first per company policy.")
        ]

        for customer in customers_with_notes:
            # 2-5 notes per customer
            num_notes = random.randint(2, 5)

            for i in range(num_notes):
                note_type, content = random.choice(note_types)

                # Promise notes have additional fields
                if note_type == "promise_to_pay":
                    promise_date = self.today + timedelta(days=random.randint(1, 14))
                    promise_amount = round(float(customer.current_balance) * random.uniform(0.3, 1.0), 2)

                    # Some promises are kept, some broken
                    if promise_date < self.today:
                        promise_status = random.choice(["kept", "broken"])
                    else:
                        promise_status = "pending"
                else:
                    promise_date = None
                    promise_amount = None
                    promise_status = None

                note = Note(
                    customer_id=customer.id,
                    user_id=self.users[0].id,  # Sarah Martinez
                    note_type=note_type,
                    content=content,
                    promise_date=promise_date,
                    promise_amount=Decimal(str(promise_amount)) if promise_amount else None,
                    promise_status=promise_status,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60))
                )

                session.add(note)
                count += 1

        await session.flush()
        return count

    async def _create_tasks(self, session):
        """Create collection tasks."""
        count = 0

        # Select customers for tasks (20% of customers)
        customers_with_tasks = random.sample(
            self.customers,
            k=int(len(self.customers) * 0.2)
        )

        task_templates = [
            ("Follow up on overdue invoice", "high"),
            ("Send statement of account", "medium"),
            ("Call to discuss payment plan", "high"),
            ("Review account for credit hold", "medium"),
            ("Schedule callback with customer", "low"),
            ("Escalate to manager", "high")
        ]

        for customer in customers_with_tasks:
            title, priority = random.choice(task_templates)

            # Due date distribution
            due_offset = random.choice([
                -5, -2, 0,  # Overdue/due today
                1, 2, 3, 7, 14  # Future
            ])
            due_date = self.today + timedelta(days=due_offset)

            # Status based on due date
            if due_offset < 0:
                status = "Open"  # Overdue
            elif due_offset == 0:
                status = "Open"  # Due today
            else:
                status = random.choice(["Open", "In Progress"])

            task = Task(
                customer_id=customer.id,
                assigned_to=self.users[0].id,  # Sarah Martinez
                title=title,
                description=f"Task for {customer.name}",
                priority=priority,
                status=status,
                due_date=due_date,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )

            session.add(task)
            count += 1

        await session.flush()
        return count

    async def _create_alerts(self, session):
        """Generate alerts for customers with issues."""
        count = 0

        for customer in self.customers:
            # Check for alert conditions
            alerts_to_create = []

            # Inactive account (120+ days no activity)
            if customer.last_invoice_date:
                days_since_invoice = (self.today - customer.last_invoice_date).days
                if days_since_invoice >= 120:
                    alerts_to_create.append(("inactive_account", "Critical"))

            # Over credit limit
            if customer.current_balance > customer.credit_limit:
                alerts_to_create.append(("over_credit_limit", "Medium"))

            # Check for 90+ day invoices
            for invoice in self.invoices:
                if invoice.customer_id == customer.id:
                    if invoice.aging_bucket == "90+ Days":
                        alerts_to_create.append(("invoice_90_plus_days", "High"))
                        break  # Only one alert per type

            # Create alerts
            for alert_type, severity in alerts_to_create:
                title, description = self._get_alert_content(alert_type, customer)

                alert = Alert(
                    customer_id=customer.id,
                    alert_type=alert_type,
                    severity=severity,
                    title=title,
                    description=description,
                    status="active",
                    created_at=datetime.now() - timedelta(days=random.randint(0, 7))
                )

                session.add(alert)
                count += 1

        await session.flush()
        return count

    def _get_alert_content(self, alert_type, customer):
        """Get alert title and description."""
        if alert_type == "inactive_account":
            days = (self.today - customer.last_invoice_date).days
            return (
                f"Account Inactive {days}+ Days",
                f"No invoice activity for {customer.name} in over {days} days. Review account status."
            )
        elif alert_type == "over_credit_limit":
            over_amount = customer.current_balance - customer.credit_limit
            return (
                f"Over Credit Limit by ${over_amount:,.2f}",
                f"{customer.name} current balance (${customer.current_balance:,.2f}) exceeds credit limit (${customer.credit_limit:,.2f})"
            )
        elif alert_type == "invoice_90_plus_days":
            return (
                "Invoice 90+ Days Overdue",
                f"{customer.name} has invoices overdue more than 90 days. Escalate to manager."
            )
        else:
            return ("Alert", "Customer requires attention")

    def _print_summary(self):
        """Print summary of created data."""
        total_ar = sum(float(inv.open_balance) for inv in self.invoices)
        overdue_ar = sum(
            float(inv.open_balance) for inv in self.invoices
            if inv.due_date and inv.due_date < self.today
        )

        print(f"\n📊 Data Summary:")
        print(f"   Users: {len(self.users)}")
        print(f"   Customers: {len(self.customers)}")
        print(f"   Invoices: {len(self.invoices)}")
        print(f"   Payments: {len(self.payments)}")
        print(f"   Total AR: ${total_ar:,.2f}")
        print(f"   Overdue AR: ${overdue_ar:,.2f}")
        print(f"   DSO (estimated): {int((overdue_ar / total_ar * 100) * 0.35) if total_ar > 0 else 0} days")


async def main():
    parser = argparse.ArgumentParser(description="Seed AR Control Hub with demo data")
    parser.add_argument(
        "--scenario",
        choices=["demo", "uat", "performance"],
        default="demo",
        help="Data scenario: demo (50 customers), uat (100), performance (1000)"
    )

    args = parser.parse_args()

    seeder = DemoDataSeeder(scenario=args.scenario)
    await seeder.seed()


if __name__ == "__main__":
    asyncio.run(main())
