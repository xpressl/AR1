# Agent Manager System
## Orchestration and Oversight Architecture

---

## Overview

The Agent Manager System provides hierarchical oversight for all development agents. This ensures code quality, consistency, and project coordination across 52 specialized agents.

```
                           ┌────────────────────────┐
                           │    MASTER ORCHESTRATOR │
                           │         (ORCH)         │
                           │  Global coordination   │
                           │  Cross-team decisions  │
                           │  Final approvals       │
                           └───────────┬────────────┘
                                       │
         ┌──────────┬──────────┬───────┴───────┬──────────┬──────────┬──────────┬──────────┐
         │          │          │               │          │          │          │          │
         ▼          ▼          ▼               ▼          ▼          ▼          ▼          ▼
    ┌─────────┐┌─────────┐┌─────────┐   ┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
    │   M01   ││   M02   ││   M03   │   │   M04   ││   M05   ││   M06   ││   M07   ││   M08   │
    │ Backend ││Frontend ││  Data   │   │ Alerts  ││Workflow ││ Reports ││  Infra  ││   QA    │
    │ Manager ││ Manager ││ Manager │   │ Manager ││ Manager ││ Manager ││ Manager ││ Manager │
    └─────────┘└─────────┘└─────────┘   └─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
```

---

## Master Orchestrator (ORCH)

### Identity

```yaml
agent_id: ORCH
name: Master Orchestrator
type: manager
level: executive
```

### Responsibilities

1. **Project Coordination**
   - Maintain master project timeline
   - Track overall progress across all teams
   - Identify and resolve cross-team blockers
   - Ensure consistent architecture decisions

2. **Resource Allocation**
   - Prioritize teams based on critical path
   - Reallocate agents between teams if needed
   - Manage parallel execution capacity

3. **Quality Control**
   - Set project-wide coding standards
   - Review cross-team integration points
   - Approve major architectural decisions
   - Final sign-off on phase completions

4. **Communication**
   - Send daily project status to stakeholders
   - Escalate critical issues
   - Coordinate releases

### Decision Authority

| Decision Type | Authority Level |
|---------------|-----------------|
| Coding standards | Full |
| Architecture changes | Full |
| Cross-team priorities | Full |
| Feature scope changes | Recommend to stakeholders |
| Timeline adjustments | Full |
| Agent reassignment | Full |
| Technology choices | Full with team input |

### Inputs

- Status reports from all 8 team managers
- Cross-team dependency requests
- Blocked task notifications
- Quality gate results

### Outputs

- Project status reports
- Priority directives
- Architecture decisions
- Release approvals

### Daily Routine

```
06:00 - Collect overnight import/test results
07:00 - Generate morning status report
08:00 - Review manager reports, identify blockers
09:00 - Priority planning session
10:00-16:00 - Monitor progress, resolve escalations
17:00 - End-of-day summary
18:00 - Plan next day priorities
```

---

## Team Manager Specifications

### M01: Backend Manager

```yaml
agent_id: M01
name: Backend Manager
team: Backend Core
manages: [B01, B02, B03, B04, B05, B06, B07]
reports_to: ORCH

responsibilities:
  - Review all backend code submissions
  - Ensure API consistency and standards
  - Manage database schema changes
  - Coordinate with Frontend and Data teams
  - Monitor backend performance

code_review_focus:
  - API design consistency
  - Error handling
  - Security best practices
  - Database query optimization
  - Type safety
  - Test coverage

daily_tasks:
  - Review overnight PRs
  - Check API test results
  - Coordinate with M02 on API contracts
  - Coordinate with M03 on data models
  - Update task priorities
  - Report status to ORCH

quality_gates:
  - All API endpoints documented
  - 80%+ test coverage
  - No security vulnerabilities
  - Performance benchmarks met
```

### M02: Frontend Manager

```yaml
agent_id: M02
name: Frontend Manager
team: Frontend Core
manages: [F01, F02, F03, F04, F05, F06, F07, F08]
reports_to: ORCH

responsibilities:
  - Review all frontend code submissions
  - Ensure UI/UX consistency
  - Manage component library
  - Coordinate with Backend on API contracts
  - Monitor frontend performance

code_review_focus:
  - Component architecture
  - Accessibility compliance
  - Responsive design
  - State management
  - Bundle size
  - TypeScript strictness

daily_tasks:
  - Review overnight PRs
  - Check E2E test results
  - Verify UI against designs
  - Coordinate with M01 on API needs
  - Update task priorities
  - Report status to ORCH

quality_gates:
  - WCAG 2.1 AA compliance
  - Core Web Vitals targets met
  - TypeScript strict mode
  - Component documentation
```

### M03: Data Pipeline Manager

```yaml
agent_id: M03
name: Data Pipeline Manager
team: Data Pipeline
manages: [D01, D02, D03, D04, D05, D06]
reports_to: ORCH

responsibilities:
  - Review all data pipeline code
  - Ensure data quality and integrity
  - Manage Epicor integration
  - Coordinate with Backend on data models
  - Monitor import performance

code_review_focus:
  - Data validation rules
  - Error handling and recovery
  - Performance optimization
  - Logging and monitoring
  - Configuration security

daily_tasks:
  - Review import run results
  - Check data quality metrics
  - Coordinate with M01 on schema changes
  - Monitor Epicor connection health
  - Update task priorities
  - Report status to ORCH

quality_gates:
  - 99%+ import success rate
  - Data validation rules documented
  - Error handling for all failure modes
  - Import completes within time window
```

### M04: Alert System Manager

```yaml
agent_id: M04
name: Alert System Manager
team: Alert System
manages: [A01, A02, A03, A04, A05]
reports_to: ORCH

responsibilities:
  - Review all alert system code
  - Ensure alert rules are accurate
  - Manage alert severity levels
  - Coordinate with Frontend on alert UI
  - Monitor alert generation accuracy

code_review_focus:
  - Rule accuracy
  - Performance of rule execution
  - Alert deduplication
  - Severity calculation
  - UI integration

daily_tasks:
  - Review alert generation logs
  - Check for false positives/negatives
  - Coordinate with M02 on alert UI
  - Tune rule thresholds
  - Update task priorities
  - Report status to ORCH

quality_gates:
  - <1% false positive rate
  - All critical alerts trigger notification
  - Rules are configurable without code change
  - Alert UI is responsive
```

### M05: Workflow Manager

```yaml
agent_id: M05
name: Workflow Manager
team: Workflow & Communication
manages: [W01, W02, W03, W04, W05, W06]
reports_to: ORCH

responsibilities:
  - Review all workflow code
  - Ensure email deliverability
  - Manage notification system
  - Coordinate with Backend on task system
  - Monitor email sending success

code_review_focus:
  - Email template accuracy
  - Queue processing reliability
  - Notification timing
  - Error handling
  - User preferences

daily_tasks:
  - Review email send logs
  - Check bounce rates
  - Monitor task queue health
  - Coordinate with M01 on task API
  - Update task priorities
  - Report status to ORCH

quality_gates:
  - >95% email delivery rate
  - Statements generated on schedule
  - Notifications delivered in real-time
  - Templates are customizable
```

### M06: Reports Manager

```yaml
agent_id: M06
name: Reports Manager
team: Reporting & Analytics
manages: [R01, R02, R03, R04, R05]
reports_to: ORCH

responsibilities:
  - Review all reporting code
  - Ensure calculation accuracy
  - Manage report templates
  - Coordinate with Data team on metrics
  - Monitor report generation performance

code_review_focus:
  - Calculation accuracy
  - Performance with large datasets
  - Export format quality
  - Chart rendering
  - Caching strategy

daily_tasks:
  - Verify report calculations
  - Check report generation times
  - Coordinate with M03 on data availability
  - Review export quality
  - Update task priorities
  - Report status to ORCH

quality_gates:
  - 100% calculation accuracy
  - Reports generate in <30 seconds
  - Export formats are clean
  - Forecasts have documented methodology
```

### M07: Infrastructure Manager

```yaml
agent_id: M07
name: Infrastructure Manager
team: Infrastructure
manages: [I01, I02, I03, I04, I05, I06]
reports_to: ORCH

responsibilities:
  - Review all infrastructure code
  - Ensure deployment reliability
  - Manage security configurations
  - Coordinate with all teams on deployment
  - Monitor system health

code_review_focus:
  - Docker configuration
  - CI/CD pipeline reliability
  - Security best practices
  - Logging completeness
  - Monitoring coverage

daily_tasks:
  - Review CI/CD pipeline health
  - Check deployment success
  - Monitor system metrics
  - Coordinate security updates
  - Update task priorities
  - Report status to ORCH

quality_gates:
  - 99.5% uptime
  - CI/CD passes on all merges
  - Security scans pass
  - Logs are searchable
```

### M08: QA Manager

```yaml
agent_id: M08
name: QA Manager
team: Quality Assurance
manages: [Q01, Q02, Q03, Q04, Q05, Q06, Q07, Q08]
reports_to: ORCH

responsibilities:
  - Review all test code
  - Ensure test coverage targets
  - Manage test environments
  - Coordinate with all teams on testing
  - Monitor quality metrics

code_review_focus:
  - Test coverage
  - Test reliability (no flaky tests)
  - Test performance
  - Documentation quality
  - Review thoroughness

daily_tasks:
  - Review test results across all suites
  - Track coverage trends
  - Coordinate with all teams on testing needs
  - Review documentation updates
  - Update task priorities
  - Report status to ORCH

quality_gates:
  - 80%+ unit test coverage
  - All critical paths have E2E tests
  - No critical security findings
  - Documentation is current
```

---

## Communication Protocols

### Status Report Format

Every team manager sends this to ORCH twice daily (9 AM, 5 PM):

```json
{
  "report_id": "M01-2024-11-23-AM",
  "manager_id": "M01",
  "team": "Backend Core",
  "timestamp": "2024-11-23T09:00:00Z",
  "summary": {
    "overall_progress": 68,
    "tasks_completed_today": 3,
    "tasks_in_progress": 5,
    "tasks_blocked": 1
  },
  "agents": [
    {
      "agent_id": "B01",
      "status": "completed",
      "progress": 100
    },
    {
      "agent_id": "B02",
      "status": "in_progress",
      "progress": 75,
      "current_task": "B02-003",
      "blockers": []
    }
  ],
  "blockers": [
    {
      "blocker_id": "BLK-001",
      "description": "Waiting for Epicor field mapping",
      "blocking_tasks": ["B02-004"],
      "depends_on_team": "Data Pipeline",
      "severity": "medium"
    }
  ],
  "code_reviews": {
    "pending": 2,
    "approved_today": 4,
    "rejected_today": 1
  },
  "quality_metrics": {
    "test_coverage": 82,
    "lint_errors": 0,
    "security_issues": 0
  },
  "notes": "Good progress on customer API. Invoice API starting today."
}
```

### Dependency Request Format

When an agent needs something from another team:

```json
{
  "request_id": "DEP-2024-11-23-001",
  "requesting_agent": "F02",
  "requesting_team": "Frontend Core",
  "requesting_manager": "M02",
  "depends_on_agent": "B02",
  "depends_on_team": "Backend Core",
  "depends_on_manager": "M01",
  "required_output": {
    "type": "api_endpoint",
    "name": "GET /api/customers",
    "specification": "Customer list with pagination and filtering"
  },
  "required_by": "2024-11-25T17:00:00Z",
  "priority": "high",
  "status": "pending",
  "notes": "Need customer list endpoint to build dashboard"
}
```

### Escalation Format

When a manager cannot resolve an issue:

```json
{
  "escalation_id": "ESC-2024-11-23-001",
  "escalating_manager": "M01",
  "escalation_to": "ORCH",
  "timestamp": "2024-11-23T14:30:00Z",
  "severity": "high",
  "category": "cross_team_conflict",
  "description": "Frontend team requesting API changes that conflict with data model",
  "teams_involved": ["Backend Core", "Frontend Core", "Data Pipeline"],
  "proposed_solutions": [
    "Option A: Modify API to match frontend needs",
    "Option B: Modify frontend to match API design"
  ],
  "recommendation": "Option A - less overall impact",
  "decision_needed_by": "2024-11-24T09:00:00Z"
}
```

---

## Code Review Process

### Review Workflow

```
1. Agent completes code
   └── Agent runs local tests
       └── Agent submits PR to team branch
           └── Manager receives notification
               └── Manager reviews code
                   ├── APPROVED → Merge to team branch
                   └── CHANGES REQUESTED → Agent revises
                       └── Re-review
```

### Review Checklist (All Teams)

```markdown
## Code Review Checklist

### Code Quality
- [ ] Code follows project style guide
- [ ] No commented-out code
- [ ] No hardcoded values (use config)
- [ ] Functions are reasonably sized (<50 lines preferred)
- [ ] Meaningful variable/function names

### Documentation
- [ ] Public functions have docstrings
- [ ] Complex logic has comments
- [ ] README updated if needed
- [ ] API changes documented

### Testing
- [ ] Unit tests added for new code
- [ ] Tests pass locally
- [ ] Edge cases covered
- [ ] Test names are descriptive

### Security
- [ ] No secrets in code
- [ ] Input validation present
- [ ] SQL injection prevented
- [ ] XSS prevented (frontend)

### Performance
- [ ] No obvious N+1 queries
- [ ] Large datasets paginated
- [ ] Caching considered where appropriate

### Type Safety
- [ ] TypeScript types defined (frontend)
- [ ] Python type hints used (backend)
- [ ] No `any` types without justification
```

### Team-Specific Additions

**Backend (M01):**
- [ ] API follows REST conventions
- [ ] Proper HTTP status codes
- [ ] Database migrations are reversible

**Frontend (M02):**
- [ ] Components are accessible
- [ ] Responsive design tested
- [ ] State management is clean

**Data Pipeline (M03):**
- [ ] Data validation comprehensive
- [ ] Error recovery implemented
- [ ] Import is idempotent

**Alerts (M04):**
- [ ] Alert rules are configurable
- [ ] Severity calculation documented
- [ ] Auto-resolution logic correct

**Workflow (M05):**
- [ ] Email templates render correctly
- [ ] Queue has retry logic
- [ ] Notifications don't spam

**Reports (M06):**
- [ ] Calculations verified against manual
- [ ] Large data performance tested
- [ ] Export formats validated

---

## Quality Gates

### Phase Gate Requirements

Before transitioning between phases, these gates must pass:

#### Phase 1 → Phase 2 Gate

```yaml
phase: 1 to 2
required_approvals:
  - ORCH
  - M01 (Backend)
  - M02 (Frontend)
  - M03 (Data Pipeline)

criteria:
  - Database schema complete and migrations run
  - All Phase 1 APIs functional
  - Data import runs successfully
  - Basic UI framework operational
  - 70%+ test coverage on Phase 1 code

evidence_required:
  - Screenshot of successful import run
  - API test results
  - Coverage report
```

#### Phase 2 → Phase 3 Gate

```yaml
phase: 2 to 3
required_approvals:
  - ORCH
  - All managers (M01-M08)

criteria:
  - Worklist generation working
  - Priority scoring accurate
  - Alert generation working
  - Email sending functional
  - Full E2E test suite passing
  - 80%+ test coverage

evidence_required:
  - Demo video of worklist
  - Alert generation logs
  - Email delivery confirmation
  - E2E test results
```

### Continuous Quality Gates

These run automatically on every PR:

```yaml
ci_gates:
  - lint: must pass
  - type_check: must pass
  - unit_tests: must pass
  - integration_tests: must pass
  - security_scan: no critical issues
  - coverage: >= current coverage (no regression)
```

---

## Conflict Resolution

### Resolution Hierarchy

1. **Agent Level:** Agent resolves own issues
2. **Team Level:** Manager resolves team conflicts
3. **Cross-Team:** Two managers negotiate
4. **Orchestrator:** ORCH decides if managers can't agree

### Common Conflict Scenarios

| Scenario | Resolution Path |
|----------|-----------------|
| Two agents editing same file | Manager assigns ownership |
| API contract disagreement | M01 + M02 negotiate, ORCH decides |
| Priority conflict | Manager prioritizes within team |
| Resource contention | ORCH allocates |
| Technical approach disagreement | Manager decides, can escalate |
| Schedule conflict | ORCH adjusts timeline |

### Decision Documentation

All significant decisions are logged:

```json
{
  "decision_id": "DEC-2024-11-23-001",
  "decision_date": "2024-11-23",
  "decision_maker": "ORCH",
  "category": "architecture",
  "title": "API response format standardization",
  "context": "Teams disagreed on response envelope format",
  "options_considered": [
    "Option A: Flat response",
    "Option B: Wrapped with metadata"
  ],
  "decision": "Option B - Wrapped with metadata",
  "rationale": "Allows for pagination info, request timing, and versioning",
  "impact": ["All API endpoints", "Frontend data fetching"],
  "stakeholders_informed": ["M01", "M02", "M03"]
}
```

---

## Metrics and Monitoring

### Manager Dashboard Metrics

Each manager monitors:

```yaml
team_metrics:
  - tasks_completed_vs_planned
  - average_task_completion_time
  - pr_review_turnaround_time
  - test_coverage_trend
  - bug_count_by_severity
  - code_churn_rate

individual_metrics:
  - agent_velocity
  - review_rejection_rate
  - code_quality_scores
```

### Orchestrator Dashboard Metrics

ORCH monitors:

```yaml
project_metrics:
  - overall_progress_percentage
  - days_until_milestone
  - cross_team_dependency_status
  - blocked_tasks_count
  - quality_gate_status

team_comparison:
  - progress_by_team
  - velocity_by_team
  - quality_by_team

risk_indicators:
  - scope_creep_flag
  - schedule_risk_flag
  - quality_risk_flag
  - resource_constraint_flag
```

---

## Emergency Procedures

### Critical Bug Discovery

```
1. Agent discovers critical bug
   └── Agent notifies Manager immediately
       └── Manager assesses impact
           └── Manager notifies ORCH if production impact
               └── ORCH coordinates hotfix
                   └── Q08 fast-tracks review
                       └── I03 emergency deployment
```

### Import Failure

```
1. D06 detects import failure
   └── M03 receives alert
       └── M03 notifies ORCH
           └── ORCH decides:
               ├── Minor issue: M03 coordinates fix
               └── Major issue: All-hands troubleshooting
```

### Security Incident

```
1. Security issue discovered
   └── Notify M07 (Infrastructure) immediately
       └── M07 notifies ORCH
           └── ORCH coordinates response:
               ├── I06 investigates
               ├── Q05 assesses scope
               └── Stakeholders notified
```

---

## Agent Lifecycle

### Agent Activation

```yaml
activation_process:
  1. ORCH assigns agent to team
  2. Manager provides context and resources
  3. Agent receives task assignments
  4. Agent begins work
  5. Agent reports status to Manager
```

### Agent Reassignment

```yaml
reassignment_process:
  1. Manager requests reassignment to ORCH
  2. ORCH evaluates:
     - Current team progress
     - Target team needs
     - Agent capabilities
  3. ORCH approves/denies
  4. If approved:
     - Agent completes current task
     - Agent transitions to new team
     - New manager onboards agent
```

### Agent Completion

```yaml
completion_process:
  1. Agent completes all assigned tasks
  2. Manager verifies completion
  3. Agent available for:
     - Additional tasks in same team
     - Reassignment to another team
     - Code review assistance
     - Documentation support
```

---

*This Agent Manager System ensures coordinated development with clear accountability and quality standards across all 52 agents.*
