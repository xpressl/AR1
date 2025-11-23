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

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Docker (recommended)

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd AR1

# Install dependencies
npm install
pip install -r requirements.txt

# Start database
docker-compose up -d postgres

# Run migrations
npm run db:migrate

# Start development server
npm run dev
```

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

## Phase Rollout

| Phase | Timeline | Features |
|-------|----------|----------|
| Phase 1 | Weeks 1-6 | Data import, dashboard, customer 360 |
| Phase 2 | Weeks 7-12 | Worklist, alerts, email automation |
| Phase 3 | Weeks 13-18 | Reports, cash forecast, analytics |
| Phase 4 | Weeks 19-24 | Payment portal, CRM integration |

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

## Contributing

See agent specifications in `docs/MULTI_AGENT_ARCHITECTURE.md` for task assignments and coding standards.

## License

Proprietary - All rights reserved

---

*Built with the AR Control Hub Multi-Agent Development System*
