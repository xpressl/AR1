# AR Control Hub

**Accounts Receivable Management System for Building Supplies**

A centralized AR workspace that sits on top of Epicor Eagle, providing prioritized worklists, automated alerts, and comprehensive customer visibility.

---

## Project Overview

AR Control Hub ingests daily data from Epicor Eagle (invoices, payments, customers, credit, aging) and provides:

- **Dashboard:** Real-time AR health metrics and aging summary
- **Prioritized Worklist:** Risk-scored collection queue
- **Customer 360:** Complete customer view with notes and history
- **Alert System:** Automated detection of inactive accounts, broken promises, credit issues
- **Statements & Communication:** Automated email statements and reminders
- **Reports:** Aging, DSO, cash forecasting, and performance metrics

## Documentation

| Document | Description |
|----------|-------------|
| [PRD](docs/PRD_AR_CONTROL_HUB.md) | Full product requirements |
| [Multi-Agent Architecture](docs/MULTI_AGENT_ARCHITECTURE.md) | 52-agent development system |
| [Task Breakdown](docs/TASK_BREAKDOWN.md) | 302 tasks across all agents |
| [Agent Manager System](docs/AGENT_MANAGER_SYSTEM.md) | Manager oversight and quality control |

## Project Structure

```
AR1/
├── docs/                          # Documentation
│   ├── PRD_AR_CONTROL_HUB.md     # Product requirements
│   ├── MULTI_AGENT_ARCHITECTURE.md
│   ├── TASK_BREAKDOWN.md
│   └── AGENT_MANAGER_SYSTEM.md
│
├── src/
│   ├── api/                       # Backend API
│   │   └── routes/               # API endpoints
│   │
│   ├── models/                   # Data models
│   │
│   ├── services/                 # Business logic
│   │   ├── alerts/              # Alert detection
│   │   ├── workflow/            # Tasks, email, notifications
│   │   └── reports/             # Report generation
│   │
│   ├── data_pipeline/           # Epicor data ingestion
│   │   ├── connectors/          # Data source connectors
│   │   ├── parsers/             # CSV parsing
│   │   ├── transformers/        # Data transformation
│   │   ├── loaders/             # Database loading
│   │   ├── validators/          # Data validation
│   │   └── scheduler/           # Import scheduling
│   │
│   ├── db/                      # Database
│   │   ├── migrations/          # Schema migrations
│   │   └── seeds/               # Seed data
│   │
│   ├── frontend/                # React/Next.js frontend
│   │   ├── pages/               # Page components
│   │   ├── components/          # UI components
│   │   ├── layouts/             # Layout components
│   │   ├── styles/              # CSS/styles
│   │   ├── hooks/               # React hooks
│   │   └── lib/                 # Utilities
│   │
│   └── templates/               # Email templates
│       └── email/
│
├── tests/                       # Test suites
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── data/
│
├── config/                      # Configuration
├── scripts/                     # Utility scripts
└── .claude/                     # Claude Code commands
    └── commands/
```

## Development Team (Agents)

### Team Structure

| Team | Manager | Agents | Focus |
|------|---------|--------|-------|
| Backend Core | M01 | B01-B07 | API, database, authentication |
| Frontend Core | M02 | F01-F08 | UI, dashboard, worklist |
| Data Pipeline | M03 | D01-D06 | Epicor integration, import |
| Alert System | M04 | A01-A05 | Alert rules, detection |
| Workflow | M05 | W01-W06 | Tasks, email, notifications |
| Reporting | M06 | R01-R05 | Reports, analytics |
| Infrastructure | M07 | I01-I06 | DevOps, security |
| QA | M08 | Q01-Q08 | Testing, documentation |

### Agent Count
- **Worker Agents:** 52
- **Manager Agents:** 8
- **Orchestrator:** 1
- **Total Tasks:** 302

## Technology Stack

### Backend
- **FastAPI 0.104+** - Modern Python web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0** - Async ORM for PostgreSQL
- **Pydantic** - Data validation and settings management
- **Alembic** - Database migrations
- **APScheduler** - Job scheduling for imports and digests
- **Jinja2** - Email template rendering
- **python-jose** - JWT token handling
- **passlib** - Password hashing (bcrypt)

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript 5.0+** - Type-safe JavaScript
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **Lucide Icons** - Modern icon library
- **React Hooks** - State management and side effects

### Database
- **PostgreSQL 14+** - Primary data store
- **Indexes** - Optimized for query performance on customer_id, invoice_date, due_date

### Infrastructure
- **Docker** - Containerization
- **Uvicorn** - ASGI server
- **CORS Middleware** - Cross-origin resource sharing

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Docker (recommended)

### Environment Setup

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ar_control_hub

# API
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
ENVIRONMENT=development
LOG_LEVEL=INFO

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@company.com
SMTP_FROM_NAME=AR Control Hub

# Data Import
EPICOR_EXPORT_PATH=/path/to/epicor/exports
ENABLE_SCHEDULER=true
IMPORT_SCHEDULE_CRON=0 6 * * *

# Notifications
DAILY_DIGEST_SCHEDULE=30 6 * * *
DIGEST_RECIPIENTS=ar-team@company.com
```

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd AR1

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Start database
docker-compose up -d postgres

# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_data.py

# Start backend API (port 8000)
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend dev server (port 3000)
npm run dev
```

### Access Points

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **API ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### Running Tests

```bash
# Unit tests
npm run test:unit

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# All tests
npm run test
```

## Implementation Status

### ✅ Phase 1: Core Infrastructure (COMPLETED)
**Timeline:** Weeks 1-6

**Features Delivered:**
- Database schema with 15+ models (customers, invoices, payments, notes, tasks, alerts)
- FastAPI REST API with JWT authentication and RBAC
- Next.js 14 frontend with TypeScript and Tailwind CSS
- Customer 360 view with complete history
- Interactive modals: Add Note, Send Email, Create Task
- Data pipeline with Epicor CSV connectors
- Validation and upsert logic for data imports
- Scheduled imports (daily at 6 AM, twice-daily option)
- Alert rules engine with 6 alert types
- Email service with customizable templates
- Dashboard with real-time AR metrics

**Key Files:**
- Models: `src/models/*.py` (customer, invoice, payment, note, task, alert, user)
- API Routes: `src/api/routes/*.py` (15+ route modules)
- Data Pipeline: `src/data_pipeline/` (connectors, validators, loaders, scheduler)
- Frontend Pages: `src/frontend/pages/` (dashboard, customers, invoices)

### ✅ Phase 2: Automation & Portals (COMPLETED)
**Timeline:** Weeks 7-12

**Features Delivered:**
- **Promise-to-Pay Tracking:** Full lifecycle management with automatic broken promise detection
- **Salesperson Portal:** Read-only view for sales team with X-Salesperson-ID authentication
- **Daily Email Digest:** HTML email summary sent at 6:30 AM with key metrics
- **In-App Notifications:** Real-time notification system with badge counts
- **Security Hardening:** Fixed critical authentication vulnerabilities

**Key Components:**
- Promise Tracking: `src/api/routes/promises.py`, `src/frontend/pages/promises/page.tsx`
- Salesperson Portal: `src/api/routes/salesperson.py`, `src/frontend/pages/salesperson/page.tsx`
- Email Digest: `src/services/notifications/daily_digest.py`
- Notifications: `src/models/notification.py`, `src/api/routes/notifications.py`

**Critical Fixes Applied:**
- Fixed Jinja2 template rendering bug in email digest (would crash in production)
- Added authentication to salesperson routes (prevented unauthorized data access)

### ✅ Phase 3: Analytics & Forecasting (COMPLETED)
**Timeline:** Weeks 13-18

**Features Delivered:**
- **Cash Flow Forecast:** 8-week rolling forecast from invoice due dates + payment promises
- **DSO Analysis:** Days Sales Outstanding calculation using Countback Method (30/60/90 day basis)
- **Trend Analysis:** Monthly DSO trending with visual charts
- **Problem Account Detection:** Identifies customers with DSO 50%+ above company average
- **Collections Performance:** Team activity tracking, promise keeping rates, weekly trends
- **Forecast Accuracy Tracking:** Historical forecast vs actual comparison

**Key Services:**
- Cash Forecast: `src/services/analytics/cash_forecast.py`
- DSO Analysis: `src/services/analytics/dso_analysis.py`
- Analytics API: `src/api/routes/analytics.py` (10+ endpoints)
- Frontend Dashboards: `src/frontend/pages/analytics/` (cash-forecast, dso)

**Business Metrics:**
- Target DSO: 35 days (industry standard for building supplies)
- Forecast Accuracy Target: 90%+
- Alert Threshold: DSO variance > 50% from average

### 🔜 Phase 4: Payment Portal & Advanced Features (PLANNED)
**Timeline:** Weeks 19-24

**Planned Features:**
- Customer payment portal
- CRM integration (Salesforce/HubSpot)
- Advanced reporting with export
- Mobile app support
- API rate limiting and caching

## Key Features

### Blinking Alerts
Critical alerts (inactive accounts 120+ days, broken promises, over credit limit) display with visual pulsing animation to immediately draw attention.

### Priority Scoring
Accounts are scored based on:
- Days past due
- Total overdue balance
- Credit utilization
- Inactive flag
- Broken promise history
- Payment patterns

### Epicor Integration
Daily data sync from Epicor Eagle via:
- CSV file export (primary)
- Direct database read (optional)
- API integration (if available)

## API Documentation

### Core Endpoints

#### Authentication (`/api/auth`)
- `POST /login` - User login, returns JWT token
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user profile

#### Customers (`/api/customers`)
- `GET /customers` - List customers with filtering and pagination
- `GET /customers/{id}` - Get customer details
- `GET /customers/{id}/invoices` - Get customer invoices
- `GET /customers/{id}/notes` - Get customer notes history
- `GET /customers/{id}/alerts` - Get customer active alerts
- `PUT /customers/{id}` - Update customer information

#### Invoices (`/api/invoices`)
- `GET /invoices` - List invoices with filters (status, customer, date range)
- `GET /invoices/{id}` - Get invoice details
- `GET /invoices/aging` - Get aging report data
- `PUT /invoices/{id}` - Update invoice

#### Payments (`/api/payments`)
- `GET /payments` - List payments with filters
- `GET /payments/{id}` - Get payment details
- `POST /payments` - Record new payment
- `GET /payments/recent` - Get recent payments (last 30 days)

#### Notes (`/api/notes`)
- `GET /notes` - List notes with filters (customer, type, date)
- `POST /notes` - Create new note (general, phone_call, promise_to_pay, email_sent)
- `PUT /notes/{id}` - Update note
- `DELETE /notes/{id}` - Delete note

#### Tasks (`/api/tasks`)
- `GET /tasks` - List tasks with filters (status, assigned_to, priority)
- `GET /tasks/my` - Get current user's tasks
- `POST /tasks` - Create new task
- `PUT /tasks/{id}` - Update task
- `PUT /tasks/{id}/complete` - Mark task complete

#### Alerts (`/api/alerts`)
- `GET /alerts` - List active alerts with filters
- `GET /alerts/summary` - Get alert counts by type and severity
- `POST /alerts/generate` - Manually trigger alert detection
- `PUT /alerts/{id}/dismiss` - Dismiss alert

#### Dashboard (`/api/dashboard`)
- `GET /dashboard/summary` - Get AR summary metrics
- `GET /dashboard/aging` - Get aging breakdown
- `GET /dashboard/activity` - Get recent activity feed
- `GET /dashboard/worklist` - Get prioritized collection worklist

### Phase 2 Endpoints

#### Promises (`/api/promises`)
- `GET /promises` - List promises with filters (status, date range)
- `GET /promises/stats` - Get promise statistics (total, kept, broken, rate)
- `GET /promises/due-soon` - Get promises due in next 7 days
- `POST /promises/detect-broken` - Auto-detect broken promises (3+ days overdue)
- `GET /promises/performance` - Get promise keeping performance by salesperson

#### Salesperson Portal (`/api/salesperson`)
**Authentication:** Requires `X-Salesperson-ID` header

- `GET /salesperson/customers` - Get assigned customers (filtered by salesperson)
- `GET /salesperson/summary` - Get salesperson AR summary
- `GET /salesperson/alerts` - Get alerts for assigned customers only
- `GET /salesperson/activity` - Get recent activity on assigned accounts

#### Notifications (`/api/notifications`)
- `GET /notifications` - Get user notifications (unread, recent)
- `GET /notifications/count` - Get unread count by severity (for badge)
- `POST /notifications` - Create notification
- `PUT /notifications/{id}/read` - Mark notification as read
- `DELETE /notifications/{id}` - Dismiss notification
- `POST /notifications/broadcast` - Send notification to multiple users (admin)

### Phase 3 Endpoints

#### Cash Flow Forecast (`/api/analytics/forecast`)
- `GET /forecast/cash` - Generate cash flow forecast
  - Query params: `weeks` (1-52), `include_promises` (bool), `group_by` (customer/salesperson/branch)
  - Returns weekly breakdown with invoice-based + promise-based projections
- `GET /forecast/accuracy` - Get historical forecast vs actual comparison
  - Query params: `months` (1-24)
  - Returns accuracy percentage and variance trends

#### DSO Analysis (`/api/analytics/dso`)
- `GET /dso/current` - Get current DSO calculation (30/60/90 day basis)
- `GET /dso/trend` - Get monthly DSO trend
  - Query params: `months` (1-24)
  - Returns monthly DSO values vs target
- `GET /dso/by-segment` - Get DSO by segment
  - Query params: `segment_type` (salesperson/customer_type/branch)
  - Returns DSO breakdown and variance from target
- `GET /dso/alerts` - Get problem accounts with high DSO
  - Returns customers with DSO 50%+ above company average

#### Collections Performance (`/api/analytics/performance`)
- `GET /performance/summary` - Get collections performance summary
  - Query params: `days` (1-90)
  - Returns calls, emails, tasks, promises, amount collected
- `GET /performance/by-user` - Get performance breakdown by AR specialist
  - Query params: `days` (1-90)
  - Returns activity metrics per user
- `GET /performance/trend` - Get weekly performance trend
  - Query params: `weeks` (1-52)
  - Returns weekly calls, payments, collections amount

#### Email (`/api/email`)
- `POST /email/send-statement` - Send customer statement
- `POST /email/send-reminder` - Send payment reminder
- `POST /email/send-custom` - Send custom email to customer

#### Imports (`/api/imports`)
- `GET /imports` - List import history
- `GET /imports/{id}` - Get import details
- `POST /imports/trigger` - Manually trigger import job
- `GET /imports/status/{job_id}` - Get import job status

#### Reports (`/api/reports`)
- `GET /reports/aging` - Generate aging report
- `GET /reports/collections` - Generate collections report
- `POST /reports/export` - Export report to CSV/PDF

### Response Format

All endpoints return JSON with consistent structure:

**Success Response:**
```json
{
  "data": { ... },
  "status": "success"
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "status": "error"
}
```

### Authentication

Protected endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

Salesperson portal requires additional header:
```
X-Salesperson-ID: <salesperson_id>
```

## Contributing

See agent specifications in `docs/MULTI_AGENT_ARCHITECTURE.md` for task assignments and coding standards.

## License

Proprietary - All rights reserved

---

**Project Stats:**
- **Lines of Code:** ~8,800+
- **API Endpoints:** 70+
- **Database Models:** 15+
- **Frontend Pages:** 20+
- **Services:** 12+
- **Development Time:** 18 weeks (Phases 1-3)

*Built with the AR Control Hub Multi-Agent Development System*
