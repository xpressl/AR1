# AR Control Hub - Quick Start Guide

## For Agents: How to Get Started

### 1. Understand Your Assignment

Each agent has a specific role. Check your agent ID prefix:
- **B** = Backend Core (database, API)
- **F** = Frontend (UI, components)
- **D** = Data Pipeline (Epicor integration)
- **A** = Alert System (rules, detection)
- **W** = Workflow (tasks, email)
- **R** = Reports (analytics)
- **I** = Infrastructure (DevOps)
- **Q** = QA (testing, docs)

### 2. Find Your Tasks

Look up your tasks in `docs/TASK_BREAKDOWN.md`. Each task has:
- Task ID (e.g., B02-003)
- Task Name
- Description
- Priority (P1 = highest)
- Estimated hours
- File locations to create/modify

### 3. Check Dependencies

Before starting, verify:
1. Dependencies from other agents are complete
2. Required APIs/data models exist
3. You have access to necessary specifications

### 4. Create Your Files

Follow the project structure:
```
src/
├── api/routes/          # API endpoints
├── models/              # Data models
├── services/            # Business logic
├── data_pipeline/       # Data import
├── frontend/            # UI components
└── templates/           # Email templates
```

### 5. Follow Standards

- **Backend**: Python with FastAPI OR Node.js with Express
- **Frontend**: Next.js 14 + TypeScript + Tailwind
- **Testing**: Jest (frontend), Pytest (backend)
- **All code**: Must include types, error handling, and tests

### 6. Submit for Review

1. Complete your task
2. Run tests locally
3. Update relevant documentation
4. Submit to your team manager (M01-M08)

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `docs/PRD_AR_CONTROL_HUB.md` | Full product requirements |
| `docs/MULTI_AGENT_ARCHITECTURE.md` | Agent organization |
| `docs/TASK_BREAKDOWN.md` | All 302 tasks |
| `docs/AGENT_MANAGER_SYSTEM.md` | Manager oversight |

---

## Common Commands

### Invoke an Agent
```
/agent-backend    # Backend tasks
/agent-frontend   # Frontend tasks
/agent-data       # Data pipeline tasks
/agent-alerts     # Alert system tasks
/agent-workflow   # Workflow tasks
/agent-reports    # Reporting tasks
/agent-infra      # Infrastructure tasks
/agent-qa         # QA tasks
```

### Run a Specific Task
```
/run-task B02-003
```

### Orchestrator Commands
```
/orchestrator status      # Project status
/orchestrator prioritize  # Adjust priorities
```

---

## Critical Features

### 1. Blinking Alerts (IMPORTANT)
Critical alerts MUST visually blink/pulse. Use this CSS:
```css
.alert-critical {
  animation: critical-pulse 1.5s ease-in-out infinite;
}
@keyframes critical-pulse {
  0%, 100% { background-color: #FEE2E2; }
  50% { background-color: #FECACA; }
}
```

### 2. Priority Scoring
Accounts are scored for worklist ordering:
- Days past due (weight: 2x)
- Total balance (weight: 1x per $1000)
- Credit utilization (weight: 0.5x)
- Inactive flag (+25 points)
- Broken promise (+30 points)

### 3. Alert Types
- `inactive_but_owing` - No purchase 90+ days
- `near_credit_limit` - >= 80% of limit
- `over_credit_limit` - Exceeds limit
- `long_overdue_60` - 60+ days past due
- `long_overdue_90` - 90+ days past due
- `broken_promise` - Promise date passed
- `unapplied_credits` - Credits not applied

---

## Phase Timeline

| Phase | Weeks | Focus |
|-------|-------|-------|
| 1 | 1-6 | Database, API, basic UI |
| 2 | 7-12 | Worklist, alerts, email |
| 3 | 13-18 | Reports, forecasting |
| 4 | 19-24 | Advanced features |

---

## Getting Help

1. Check your agent command file (`.claude/commands/agent-*.md`)
2. Review the PRD for requirements
3. Check task breakdown for specifications
4. Escalate to your manager (M01-M08)
5. Critical issues go to Orchestrator (ORCH)
