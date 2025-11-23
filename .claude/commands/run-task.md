# Run Task Command

Execute a specific task from the AR Control Hub task breakdown.

## Usage
```
/run-task [TASK_ID]
```

## Task ID Format
`{AGENT_ID}-{TASK_NUMBER}`

Examples:
- `B01-001` - Create customers table (Database Schema Agent)
- `F02-003` - Aging chart (Dashboard Agent)
- `A02-001` - Inactive detection rule (Inactive Account Agent)

## Task Lookup

### Backend Core (B01-B07)
| Agent | Focus | Task Range |
|-------|-------|------------|
| B01 | Database Schema | B01-001 to B01-008 |
| B02 | Customer API | B02-001 to B02-006 |
| B03 | Invoice API | B03-001 to B03-006 |
| B04 | Payment API | B04-001 to B04-005 |
| B05 | Notes API | B05-001 to B05-006 |
| B06 | Authentication | B06-001 to B06-006 |
| B07 | Integration | B07-001 to B07-005 |

### Frontend Core (F01-F08)
| Agent | Focus | Task Range |
|-------|-------|------------|
| F01 | UI Framework | F01-001 to F01-008 |
| F02 | Dashboard | F02-001 to F02-008 |
| F03 | Worklist | F03-001 to F03-008 |
| F04 | Customer 360 | F04-001 to F04-010 |
| F05 | Invoice Detail | F05-001 to F05-006 |
| F06 | Notes/Activity | F06-001 to F06-006 |
| F07 | Search/Filter | F07-001 to F07-005 |
| F08 | Navigation | F08-001 to F08-005 |

### Data Pipeline (D01-D06)
| Agent | Focus | Task Range |
|-------|-------|------------|
| D01 | Epicor Connector | D01-001 to D01-006 |
| D02 | CSV Parser | D02-001 to D02-006 |
| D03 | Data Transformer | D03-001 to D03-006 |
| D04 | Data Loader | D04-001 to D04-006 |
| D05 | Data Validator | D05-001 to D05-006 |
| D06 | Import Scheduler | D06-001 to D06-005 |

### Alert System (A01-A05)
| Agent | Focus | Task Range |
|-------|-------|------------|
| A01 | Rules Engine | A01-001 to A01-006 |
| A02 | Inactive Account | A02-001 to A02-005 |
| A03 | Credit Limit | A03-001 to A03-005 |
| A04 | Promise Tracker | A04-001 to A04-006 |
| A05 | Alert UI | A05-001 to A05-006 |

### Workflow (W01-W06)
| Agent | Focus | Task Range |
|-------|-------|------------|
| W01 | Task Manager | W01-001 to W01-007 |
| W02 | Email Template | W02-001 to W02-006 |
| W03 | Statement Gen | W03-001 to W03-006 |
| W04 | Email Sender | W04-001 to W04-006 |
| W05 | Notification | W05-001 to W05-006 |
| W06 | Dispute Workflow | W06-001 to W06-007 |

### Reporting (R01-R05)
| Agent | Focus | Task Range |
|-------|-------|------------|
| R01 | Aging Report | R01-001 to R01-005 |
| R02 | DSO Calculator | R02-001 to R02-005 |
| R03 | Cash Forecast | R03-001 to R03-005 |
| R04 | Performance Report | R04-001 to R04-005 |
| R05 | Export | R05-001 to R05-005 |

### Infrastructure (I01-I06)
| Agent | Focus | Task Range |
|-------|-------|------------|
| I01 | Docker Setup | I01-001 to I01-005 |
| I02 | Database Admin | I02-001 to I02-005 |
| I03 | CI/CD Pipeline | I03-001 to I03-006 |
| I04 | Logging | I04-001 to I04-005 |
| I05 | Monitoring | I05-001 to I05-005 |
| I06 | Security | I06-001 to I06-004 |

### QA (Q01-Q08)
| Agent | Focus | Task Range |
|-------|-------|------------|
| Q01 | Unit Test | Q01-001 to Q01-006 |
| Q02 | Integration Test | Q02-001 to Q02-006 |
| Q03 | E2E Test | Q03-001 to Q03-006 |
| Q04 | Performance Test | Q04-001 to Q04-006 |
| Q05 | Security Test | Q05-001 to Q05-006 |
| Q06 | Data Quality Test | Q06-001 to Q06-006 |
| Q07 | Documentation | Q07-001 to Q07-006 |
| Q08 | Code Review | Q08-001 to Q08-006 |

## Execution
When you run a task:
1. Load the agent specification for the task prefix
2. Read the task details from `docs/TASK_BREAKDOWN.md`
3. Execute the task following standards
4. Create the required files
5. Write tests if applicable
6. Submit for review

## Full Task Details
See `docs/TASK_BREAKDOWN.md` for complete task specifications.
