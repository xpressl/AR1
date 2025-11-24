# AR Control Hub - Quick Start Guide

Get up and running with AR Control Hub in 10 minutes.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git

## 5-Minute Setup

### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd AR1

# Install backend dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
npm install
```

### 2. Setup Database

```bash
# Start PostgreSQL (if using Docker)
docker run --name ar-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:14

# Or install locally and create database
createdb ar_control_hub
```

### 3. Configure Environment

Create `.env` file in project root:

```bash
# Minimal configuration for local development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ar_control_hub
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
JWT_SECRET_KEY=dev-secret-key-change-in-production
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ENABLE_SCHEDULER=false
```

### 4. Run Migrations

```bash
source venv/bin/activate
alembic upgrade head
```

### 5. Start Development Servers

**Terminal 1 - Backend API:**
```bash
source venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### 6. Access the Application

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

## Create Test User

```bash
source venv/bin/activate
python3 << EOF
import asyncio
from src.db.connection import get_db
from src.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    async for db in get_db():
        user = User(
            email="admin@test.com",
            full_name="Test Admin",
            role="ar_manager",
            hashed_password=pwd_context.hash("password123"),
            is_active=True
        )
        db.add(user)
        await db.commit()
        print(f"Created user: {user.email} / password123")
        break

asyncio.run(create_user())
EOF
```

## Load Sample Data (Optional)

```bash
source venv/bin/activate
python scripts/seed_sample_data.py
```

This creates:
- 50 sample customers
- 200 sample invoices
- 100 sample payments
- Various notes and tasks

## Common Development Tasks

### Run Tests
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# All tests with coverage
pytest --cov=src tests/
```

### Format Code
```bash
# Python formatting
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/
```

### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# View migration history
alembic history
```

### Manual Data Import

Place CSV files in `data/imports/`:
- `customers.csv`
- `invoices.csv`
- `payments.csv`

```bash
# Trigger import via API
curl -X POST http://localhost:8000/api/imports/trigger
```

## Key Features to Test

### 1. Dashboard
Navigate to http://localhost:3000
- View AR summary metrics
- See aging breakdown
- Check worklist with priority scores

### 2. Customer 360
Click any customer to see:
- Invoice list with aging
- Payment history
- Notes and communication log
- Active alerts
- Quick actions (Add Note, Send Email, Create Task)

### 3. Alerts
Navigate to Alerts page:
- View critical alerts (with blinking animation)
- Filter by type and severity
- Dismiss alerts

### 4. Promise-to-Pay Tracking
Navigate to Promises page:
- View pending promises
- See overdue promises (blinking animation)
- Mark promises kept/broken

### 5. Salesperson Portal
Navigate to Salesperson Portal:
- View assigned customers only
- See AR summary for your accounts
- Limited to read-only access

### 6. Analytics Dashboards

**Cash Flow Forecast:**
- http://localhost:3000/analytics/cash-forecast
- 8-week forecast with invoice + promise data
- Toggle promise inclusion
- View weekly breakdown table

**DSO Analysis:**
- http://localhost:3000/analytics/dso
- Current DSO with 30/60/90 day basis
- Monthly trend chart
- Problem accounts list

## API Testing with Swagger

Visit http://localhost:8000/docs for interactive API documentation.

### Get Access Token
1. Click "Authorize" button
2. Use credentials: `admin@test.com` / `password123`
3. Token will be stored for all subsequent requests

### Test Key Endpoints

**Dashboard:**
```
GET /api/dashboard/summary
GET /api/dashboard/worklist
```

**Customers:**
```
GET /api/customers
GET /api/customers/{id}
GET /api/customers/{id}/invoices
```

**Analytics:**
```
GET /api/analytics/forecast/cash?weeks=8&include_promises=true
GET /api/analytics/dso/current
GET /api/analytics/dso/trend?months=12
GET /api/analytics/performance/summary?days=30
```

## Project Structure Overview

```
AR1/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # App entry point
│   │   └── routes/            # API endpoints (15+ modules)
│   │
│   ├── models/                # SQLAlchemy models (15+ tables)
│   │   ├── customer.py
│   │   ├── invoice.py
│   │   └── ...
│   │
│   ├── services/              # Business logic
│   │   ├── alerts/            # Alert detection rules
│   │   ├── analytics/         # DSO & forecasting
│   │   ├── workflow/          # Tasks & notifications
│   │   └── email/             # Email service
│   │
│   ├── data_pipeline/         # Epicor data import
│   │   ├── connectors/        # CSV connector
│   │   ├── validators/        # Data validation
│   │   └── loaders/           # Database loaders
│   │
│   └── frontend/              # Next.js application
│       ├── pages/             # Page components
│       ├── components/        # Reusable UI components
│       └── lib/               # Utilities
│
├── docs/                      # Documentation
├── tests/                     # Test suites
└── alembic/                   # Database migrations
```

## Development Tips

### Hot Reload
Both backend and frontend support hot reload:
- Backend: Code changes auto-reload with `--reload` flag
- Frontend: Next.js dev server auto-reloads on save

### Debugging

**Backend (Python):**
```python
import pdb; pdb.set_trace()  # Add breakpoint
```

**Frontend (Browser):**
```javascript
debugger;  // Add breakpoint
```

### Database Inspection
```bash
# Connect to database
psql postgresql://postgres:postgres@localhost:5432/ar_control_hub

# Common queries
\dt                              # List tables
\d customers                     # Describe table
SELECT COUNT(*) FROM invoices;   # Count records
```

### VS Code Extensions (Recommended)
- Python
- Pylance
- ESLint
- Prettier
- PostgreSQL
- REST Client

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Restart PostgreSQL
# Linux: sudo systemctl restart postgresql
# Mac: brew services restart postgresql
# Docker: docker restart ar-postgres
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
npm install
```

### Migration Conflicts
```bash
# Reset database (WARNING: destroys data)
alembic downgrade base
alembic upgrade head
```

## Next Steps

1. **Customize Alert Rules** - Edit `src/services/alerts/alert_rules.py`
2. **Add Email Templates** - Create templates in `src/templates/email/`
3. **Configure Epicor Import** - Setup CSV export mapping
4. **Customize Dashboard** - Modify `src/frontend/pages/dashboard/page.tsx`
5. **Add Business Logic** - Create new services in `src/services/`

## Resources

- **Full Documentation:** `README.md`
- **Deployment Guide:** `DEPLOYMENT.md`
- **API Docs:** http://localhost:8000/docs
- **PRD:** `docs/PRD_AR_CONTROL_HUB.md`
- **Architecture:** `docs/MULTI_AGENT_ARCHITECTURE.md`

## Support

For issues or questions:
1. Check `DEPLOYMENT.md` troubleshooting section
2. Review API docs at `/docs`
3. Inspect logs in `logs/` directory
4. Contact development team

---

**Happy Coding!** 🚀

Built with FastAPI, Next.js, PostgreSQL, and ❤️
