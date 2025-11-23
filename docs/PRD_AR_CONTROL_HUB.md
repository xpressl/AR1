# AR Control Hub - Product Requirements Document
## Building Supplies Accounts Receivable Management System

**Version:** 1.0
**Date:** November 2024
**Status:** Planning Phase

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Critical Data Analysis - Epicor Eagle](#2-critical-data-analysis)
3. [Product Vision & Objectives](#3-product-vision--objectives)
4. [User Roles & Permissions](#4-user-roles--permissions)
5. [Core Features](#5-core-features)
6. [Data Architecture](#6-data-architecture)
7. [Automation & Agent System](#7-automation--agent-system)
8. [Alert & Notification System](#8-alert--notification-system)
9. [UI/UX Requirements](#9-uiux-requirements)
10. [Integration Requirements](#10-integration-requirements)
11. [Non-Functional Requirements](#11-non-functional-requirements)
12. [Phased Rollout Plan](#12-phased-rollout-plan)
13. [Success Metrics & KPIs](#13-success-metrics--kpis)

---

## 1. Executive Summary

### 1.1 Product Name
**AR Control Hub** - Accounts Receivable Management System for Building Supplies

### 1.2 Purpose
A centralized AR workspace that sits on top of Epicor Eagle, ingesting daily data (invoices, payments, customers, credit, aging) to provide AR staff and management with:
- Clear, actionable dashboards
- Prioritized worklists
- Automated follow-up tools
- Risk alerts and notifications

**Key Principle:** Epicor Eagle remains the accounting system of record. AR Control Hub is read-only for financial data.

### 1.3 Problem Statement
Current AR challenges in building supplies operations:
- Manual report exports and spreadsheet tracking
- No prioritized call lists (random calling from aging reports)
- Disconnected AR and sales teams
- No systematic tracking of promises, disputes, and follow-ups
- Delayed identification of problem accounts
- Poor visibility into inactive customers with outstanding balances

### 1.4 Solution Overview
An intelligent AR management layer that:
- Automatically ingests data from Epicor Eagle daily
- Generates prioritized worklists based on configurable rules
- Provides visual alerts for high-risk accounts (including "blinking" notifications)
- Tracks all interactions, promises, and disputes
- Connects AR visibility with sales teams
- Automates statement generation and reminder emails

---

## 2. Critical Data Analysis - Epicor Eagle

### 2.1 TIER 1: MISSION-CRITICAL DATA (Must Have)

These fields are absolutely essential. Without them, the system cannot function.

#### Customer Master - Critical Fields
| Field | Importance | Why Critical |
|-------|------------|--------------|
| `customer_id` | CRITICAL | Primary key - links everything |
| `customer_name` | CRITICAL | Identification for all interactions |
| `credit_limit` | CRITICAL | Risk assessment, hold decisions |
| `current_balance` | CRITICAL | Core AR metric |
| `terms_code` | CRITICAL | Due date calculations |
| `customer_status` | CRITICAL | Active/Inactive/Hold/COD flags |
| `salesperson_id` | CRITICAL | Route alerts, accountability |
| `billing_email` | CRITICAL | Statement delivery |
| `billing_phone` | CRITICAL | Collection calls |

#### AR Open Items - Critical Fields
| Field | Importance | Why Critical |
|-------|------------|--------------|
| `invoice_number` | CRITICAL | Primary identifier |
| `customer_id` | CRITICAL | Links to customer |
| `invoice_date` | CRITICAL | Age calculations |
| `due_date` | CRITICAL | Overdue determination |
| `original_amount` | CRITICAL | Invoice value |
| `open_balance` | CRITICAL | What's actually owed |
| `invoice_type` | CRITICAL | Invoice vs credit memo vs finance charge |

#### Payment Data - Critical Fields
| Field | Importance | Why Critical |
|-------|------------|--------------|
| `payment_id` | CRITICAL | Tracking reference |
| `customer_id` | CRITICAL | Links to customer |
| `payment_date` | CRITICAL | Cash flow tracking |
| `payment_amount` | CRITICAL | Amount received |
| `applied_invoices` | CRITICAL | What got paid |
| `unapplied_amount` | CRITICAL | Cleanup needed |

### 2.2 TIER 2: HIGH-IMPORTANCE DATA (Should Have)

These significantly improve AR effectiveness.

| Field | Importance | Purpose |
|-------|------------|---------|
| `last_invoice_date` | HIGH | Inactive customer detection |
| `last_payment_date` | HIGH | Payment pattern analysis |
| `credit_hold_flag` | HIGH | Risk visibility |
| `hold_reason_code` | HIGH | Context for holds |
| `contact_name` | HIGH | Personal communication |
| `branch_id` | HIGH | Multi-location filtering |
| `department` | HIGH | Segment analysis |
| `payment_type` | HIGH | ACH/Check/Card tracking |
| `job_po_reference` | HIGH | Dispute resolution |
| `tax_status` | HIGH | Billing accuracy |

### 2.3 TIER 3: VALUABLE ENHANCEMENTS (Nice to Have)

| Field | Value | Purpose |
|-------|-------|---------|
| `customer_type` | MEDIUM | Contractor/Developer/DIY segmentation |
| `trade_name_dba` | MEDIUM | Alternative identification |
| `secondary_contacts` | MEDIUM | Multiple touchpoints |
| `delivery_address` | MEDIUM | Shipment verification |
| `order_ticket_number` | MEDIUM | Detailed dispute research |
| `sales_last_90_days` | MEDIUM | Activity trending |
| `average_days_to_pay` | MEDIUM | Pattern identification |

### 2.4 Data Quality Requirements

**BEFORE GO-LIVE, EPICOR DATA MUST BE CLEANED:**
- [ ] No duplicate customer IDs
- [ ] All active customers have valid email OR phone
- [ ] Credit limits set for all credit customers
- [ ] Terms codes standardized
- [ ] Inactive accounts properly flagged
- [ ] Salesperson assigned to all accounts

---

## 3. Product Vision & Objectives

### 3.1 Vision Statement
"One source of truth for AR, where every action is data-driven, prioritized, and documented."

### 3.2 Core Principles

1. **Single Source of Truth**
   - Epicor is the accounting backbone
   - AR Control Hub reads from it daily
   - Never "free-type" balances

2. **Rules Over Gut Feel**
   - Clear rules for credit limits, payment terms
   - Defined triggers for calls, holds, statements
   - Consistent enforcement

3. **Worklists Over Random Calling**
   - Daily prioritized call lists
   - Risk-scored accounts
   - No more scanning aging reports

4. **AR-Sales Connection**
   - Sales sees AR flags for their customers
   - AR sees salesperson for each account
   - Shared visibility, shared accountability

5. **Document Everything**
   - Every promise, dispute, adjustment logged
   - Timestamps and user attribution
   - Full audit trail

### 3.3 Business Objectives

| Objective | Target | Timeline |
|-----------|--------|----------|
| Reduce DSO | -5 to -10 days | 6 months |
| Increase "Current" AR | +15% | 6 months |
| Reduce 90+ day AR | -30% | 6 months |
| AR staff efficiency | +40% | 3 months |
| Collection call documentation | 100% | Immediate |

---

## 4. User Roles & Permissions

### 4.1 Role Definitions

#### AR Specialist
**Primary User** - Daily AR operations
- Access: Full worklist, customer 360, notes, tasks, statements
- Actions: Log calls, add notes, set follow-ups, send statements, mark disputes
- Restrictions: Cannot modify credit limits, cannot write-off

#### AR Manager / Controller
**Supervisory** - Oversight and approvals
- Access: All AR Specialist permissions + reports, settings, rule configuration
- Actions: Approve adjustments, modify credit limits, approve write-offs, configure alert rules
- Special: Can see all users' activities

#### Sales Representative
**Limited Access** - Customer visibility only
- Access: AR status for assigned customers, notes (read), alerts
- Actions: Add notes, view invoices, request credit limit changes
- Restrictions: Cannot send statements, cannot modify AR data

#### Inside Sales
**Expanded Sales** - Order and credit coordination
- Access: Same as Sales Rep + credit hold queue
- Actions: Request hold releases, add urgent notes
- Restrictions: Cannot release holds directly

#### Branch Manager / Owner
**Executive View** - High-level oversight
- Access: Dashboards, KPIs, exception reports
- Actions: View only, drill-down capability
- Focus: Metrics and exceptions, not daily operations

### 4.2 Permission Matrix

| Feature | AR Spec | AR Mgr | Sales | Inside | Owner |
|---------|---------|--------|-------|--------|-------|
| View Dashboard | Full | Full | Limited | Limited | Full |
| View Customer 360 | All | All | Assigned | Assigned | All |
| Add Notes | Yes | Yes | Yes | Yes | No |
| Log Calls | Yes | Yes | No | No | No |
| Send Statements | Yes | Yes | No | No | No |
| Mark Disputes | Yes | Yes | No | No | No |
| Modify Credit Limit | No | Yes | No | No | No |
| Configure Rules | No | Yes | No | No | No |
| View Reports | Limited | Full | No | No | Full |
| Approve Write-offs | No | Yes | No | No | No |

---

## 5. Core Features

### 5.1 AR Dashboard

**Purpose:** Single screen to assess AR health and prioritize focus.

#### Components:

**A. Header Metrics Bar**
- Total AR Balance (with 7-day and 30-day trend arrows)
- Total Past Due Amount
- 90+ Days Balance (highlighted if above threshold)
- Today's Expected Cash
- Last Data Import Timestamp

**B. Aging Summary Visualization**
```
[Current    ] [1-30 Days] [31-60 Days] [61-90 Days] [90+ Days]
   $450K        $120K        $45K         $18K        $12K
    70%          18%          7%           3%          2%
```
- Color-coded bars (green to red gradient)
- Click any bucket to drill down

**C. Alert Tiles (with counts and totals)**

| Tile | Display | Click Action |
|------|---------|--------------|
| Inactive But Owing | Count: 12, Total: $34,500 | Shows list |
| Broken Promises | Count: 5, Total: $28,000 | Shows list |
| Over Credit Limit | Count: 8, Total: $156,000 | Shows list |
| Near Credit Limit (>80%) | Count: 15 | Shows list |
| Unapplied Credits | Count: 23, Total: $12,400 | Shows list |
| Long Overdue (90+) | Count: 45, Total: $12,000 | Shows list |

**D. Top 10 Lists**
- Top 10 Overdue by Balance
- Top 10 Oldest Invoices
- Top 10 Over Credit Limit

**E. Filter Panel**
- Branch / Location
- Department (Doors, Trim, Decking, Framing, Hardware)
- Salesperson
- Customer Type
- Date Range

---

### 5.2 Prioritized Collections Worklist

**Purpose:** Daily call list ranked by risk and impact.

#### Priority Scoring Algorithm

```
Priority Score =
    (Oldest_Invoice_Days_Past_Due × 2) +
    (Total_Past_Due_Balance / 1000) +
    (Credit_Utilization_Percent × 0.5) +
    (Inactive_Flag × 25) +
    (Broken_Promise_Flag × 30) +
    (Payment_Pattern_Risk × 15) +
    (Customer_Value_Tier × -5)
```

#### Worklist Columns

| Column | Description |
|--------|-------------|
| Priority | Score with color indicator (Red/Yellow/Green) |
| Customer | Name with status icons |
| Total Open | Current AR balance |
| Past Due | Amount past due date |
| Oldest Days | Days since oldest invoice due |
| Credit Limit | Limit with utilization bar |
| Alert Icons | Visual flags for risks |
| Last Contact | Date of last logged interaction |
| Next Follow-up | Scheduled follow-up date |
| Owner | Assigned AR person |

#### Worklist Actions
- Click row → Open Customer 360
- Bulk select → Send statements
- Quick note → Add without opening full view
- Snooze → Defer to specific date with reason

#### View Modes
- By Account (grouped)
- By Invoice (individual)
- My Assigned Only
- Unassigned

---

### 5.3 Customer 360 View

**Purpose:** Complete customer picture before any interaction.

#### Layout:

**HEADER SECTION**
```
┌─────────────────────────────────────────────────────────────────────┐
│ [STATUS BADGE]  CUSTOMER NAME                          Customer ID  │
│ ⚠️ INACTIVE     ABC Building Supply Inc.               CUST-12345   │
│                                                                     │
│ Contact: John Smith          Phone: (555) 123-4567                 │
│ Email: john@abcbuilding.com  Salesperson: Mike Johnson             │
│                                                                     │
│ Terms: Net 30    Credit Limit: $50,000    Balance: $47,500 (95%)   │
│ [████████████████████████████████████████████░░] ← Visual bar      │
└─────────────────────────────────────────────────────────────────────┘
```

**ALERT BANNER (if any alerts active)**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🔴 CRITICAL ALERTS:                                                 │
│ • Inactive 120+ days with $47,500 balance [BLINKING]               │
│ • Over 90% credit utilization                                       │
│ • Broken promise: $15,000 due 11/15, not received                  │
└─────────────────────────────────────────────────────────────────────┘
```

**LEFT PANEL - Financial Summary**
```
Aging Breakdown:
├── Current:    $12,500
├── 1-30 Days:  $15,000
├── 31-60 Days: $8,000
├── 61-90 Days: $7,000
└── 90+ Days:   $5,000
    TOTAL:      $47,500

Open Invoices (12):
┌──────────┬────────────┬───────────┬──────────┬─────────┐
│ Invoice  │ Date       │ Due Date  │ Balance  │ Status  │
├──────────┼────────────┼───────────┼──────────┼─────────┤
│ INV-9901 │ 08/15/2024 │ 09/14/24  │ $5,000   │ 90+ ⚠️  │
│ INV-9956 │ 09/01/2024 │ 10/01/24  │ $7,000   │ 60-90   │
│ INV-10012│ 09/20/2024 │ 10/20/24  │ $8,000   │ 31-60   │
│ ...      │            │           │          │         │
└──────────┴────────────┴───────────┴──────────┴─────────┘
```

**RIGHT PANEL - Activity & Notes**
```
Activity Timeline:
┌─────────────────────────────────────────────────────────────────────┐
│ 📞 11/20/2024 10:30 AM - Sarah (AR)                                │
│ Called, spoke with John. Claims check mailed 11/18 for $15,000.    │
│ Promise to pay remaining $32,500 by 12/01.                         │
│ [Promise Logged: $32,500 by 12/01/2024]                            │
├─────────────────────────────────────────────────────────────────────┤
│ 📧 11/15/2024 09:00 AM - SYSTEM                                    │
│ Statement emailed to john@abcbuilding.com                          │
├─────────────────────────────────────────────────────────────────────┤
│ 📞 11/10/2024 02:15 PM - Sarah (AR)                                │
│ Left voicemail requesting callback regarding past due balance.      │
├─────────────────────────────────────────────────────────────────────┤
│ ⚠️ 11/01/2024 - SYSTEM ALERT                                       │
│ Account flagged as INACTIVE (no purchases 90+ days)                │
└─────────────────────────────────────────────────────────────────────┘

Open Tasks:
┌─────────────────────────────────────────────────────────────────────┐
│ ☐ Follow up on $15,000 check - Due: 11/25/2024                     │
│ ☐ Verify promise to pay $32,500 - Due: 12/02/2024                  │
└─────────────────────────────────────────────────────────────────────┘
```

**QUICK ACTIONS BAR**
```
[📞 Log Call] [📧 Send Email] [📄 Send Statement] [📝 Add Note]
[⏰ Schedule Follow-up] [⚠️ Mark Dispute] [🔒 Request Hold]
```

---

### 5.4 Invoice Detail View

**Purpose:** Deep dive into specific invoice issues.

#### Information Displayed:
- Invoice header (number, date, due date, amount, balance)
- Line items (Phase 2)
- Job/PO/Project reference
- Delivery information
- Department and salesperson
- Payment history against this invoice
- Dispute history
- Related documents (if attached)

#### Actions:
- Email invoice copy
- Mark as disputed (with reason codes)
- Add invoice-specific note
- View delivery ticket (if integrated)
- Request credit memo

---

### 5.5 Statements & Email Automation

#### Statement Features:
- **Generation:** Pull from imported balances (never manual entry)
- **Frequency:** Configurable (monthly on day X, weekly for past due)
- **Delivery:** Email (primary), Print queue (secondary)
- **Content:** Open invoices, aging summary, payment instructions

#### Email Templates:

| Template | Trigger | Tone |
|----------|---------|------|
| Friendly Reminder | 1-30 days past due | Polite, helpful |
| Second Notice | 31-60 days past due | Firm, concerned |
| Urgent Notice | 60+ days past due | Serious, action required |
| Pre-Due Reminder | Large invoices, 7 days before due | Informational |
| Statement | Monthly/On-demand | Professional |
| Promise Reminder | 3 days before promise date | Friendly reminder |

#### Compliance:
- BCC/logging for all outbound emails
- Bounce tracking
- Opt-out handling
- Template approval workflow

---

### 5.6 Cash Forecast & Reporting

#### Cash Forecast:
- Based on due dates + logged promises
- 4-8 week rolling forecast
- Broken down by: Customer, Department, Salesperson, Branch

#### Standard Reports:

| Report | Frequency | Audience |
|--------|-----------|----------|
| Aging Report with Trends | Daily/Weekly | AR Team |
| DSO by Department | Weekly | Management |
| DSO by Salesperson | Weekly | Sales Management |
| Collections Performance | Weekly | AR Manager |
| Problem Accounts | Weekly | AR Manager |
| Broken Promises | Daily | AR Team |
| Cash Receipts Summary | Daily | Controller |
| Credit Limit Utilization | Weekly | Credit Manager |

#### Export Options:
- PDF (formatted)
- Excel (raw data)
- CSV (integration)
- Scheduled email delivery

---

## 6. Data Architecture

### 6.1 Database Schema

```sql
-- Core Tables

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    epicor_customer_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    dba_trade_name VARCHAR(255),
    billing_address_line1 VARCHAR(255),
    billing_address_line2 VARCHAR(255),
    billing_city VARCHAR(100),
    billing_state VARCHAR(50),
    billing_zip VARCHAR(20),
    billing_email VARCHAR(255),
    billing_phone VARCHAR(50),
    primary_contact_name VARCHAR(255),
    salesperson_id VARCHAR(50),
    salesperson_name VARCHAR(255),
    terms_code VARCHAR(20),
    credit_limit DECIMAL(15,2),
    current_balance DECIMAL(15,2),
    status VARCHAR(20), -- Active, Inactive, On Hold, COD
    customer_type VARCHAR(50), -- Contractor, Developer, DIY, etc.
    branch_id VARCHAR(50),
    department VARCHAR(100),
    tax_status VARCHAR(20),
    tax_exempt_number VARCHAR(50),
    last_invoice_date DATE,
    last_payment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP
);

CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    epicor_invoice_number VARCHAR(50) UNIQUE NOT NULL,
    epicor_customer_id VARCHAR(50) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    original_amount DECIMAL(15,2) NOT NULL,
    open_balance DECIMAL(15,2) NOT NULL,
    status VARCHAR(20), -- Open, Paid, Partial, Disputed, Written Off
    invoice_type VARCHAR(20), -- Invoice, Credit Memo, Finance Charge
    branch_id VARCHAR(50),
    department VARCHAR(100),
    salesperson_id VARCHAR(50),
    job_reference VARCHAR(100),
    po_reference VARCHAR(100),
    project_reference VARCHAR(100),
    order_number VARCHAR(50),
    ticket_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP,
    FOREIGN KEY (epicor_customer_id) REFERENCES customers(epicor_customer_id)
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    epicor_payment_id VARCHAR(50) UNIQUE NOT NULL,
    epicor_customer_id VARCHAR(50) NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    payment_type VARCHAR(20), -- Check, ACH, Card, Cash, Wire
    check_number VARCHAR(50),
    reference_number VARCHAR(100),
    unapplied_amount DECIMAL(15,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP,
    FOREIGN KEY (epicor_customer_id) REFERENCES customers(epicor_customer_id)
);

CREATE TABLE payment_applications (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL,
    invoice_id INTEGER NOT NULL,
    amount_applied DECIMAL(15,2) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES payments(id),
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    invoice_id INTEGER, -- nullable, for customer-level notes
    user_id INTEGER NOT NULL,
    note_type VARCHAR(30), -- call, email, dispute, internal, promise_to_pay
    content TEXT NOT NULL,
    promise_amount DECIMAL(15,2), -- if promise_to_pay
    promise_date DATE, -- if promise_to_pay
    promise_status VARCHAR(20), -- pending, kept, broken
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    invoice_id INTEGER,
    assigned_to_user_id INTEGER NOT NULL,
    task_type VARCHAR(30), -- collection_call, follow_up, dispute_resolution, review
    description TEXT,
    due_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20), -- Open, Completed, Canceled, Snoozed
    priority INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    invoice_id INTEGER,
    alert_type VARCHAR(50), -- inactive_but_owing, near_credit_limit, over_credit_limit,
                            -- broken_promise, long_overdue_60, long_overdue_90,
                            -- unapplied_credits, credit_hold
    severity VARCHAR(20), -- Low, Medium, High, Critical
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by_user_id INTEGER,
    resolution_note TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE disputes (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    invoice_id INTEGER NOT NULL,
    reason_code VARCHAR(50), -- pricing, damaged, short_ship, wrong_item, tax, duplicate, other
    description TEXT,
    disputed_amount DECIMAL(15,2),
    status VARCHAR(20), -- Open, In Review, Resolved, Rejected
    assigned_to_user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_note TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);

CREATE TABLE email_log (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    invoice_id INTEGER,
    email_type VARCHAR(30), -- statement, reminder, notice, custom
    template_used VARCHAR(50),
    recipient_email VARCHAR(255),
    subject VARCHAR(255),
    body TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_by_user_id INTEGER,
    delivery_status VARCHAR(20), -- sent, delivered, bounced, failed
    opened_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE import_runs (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    status VARCHAR(20), -- Running, Success, Failed, Partial
    error_message TEXT,
    customers_imported INTEGER DEFAULT 0,
    customers_updated INTEGER DEFAULT 0,
    invoices_imported INTEGER DEFAULT 0,
    invoices_updated INTEGER DEFAULT 0,
    payments_imported INTEGER DEFAULT 0,
    alerts_generated INTEGER DEFAULT 0,
    alerts_resolved INTEGER DEFAULT 0
);

CREATE TABLE credit_holds (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    placed_by_user_id INTEGER NOT NULL,
    reason_code VARCHAR(50),
    reason_note TEXT,
    released_at TIMESTAMP,
    released_by_user_id INTEGER,
    release_note TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(30), -- ar_specialist, ar_manager, sales_rep, inside_sales, owner
    branch_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_customers_status ON customers(status);
CREATE INDEX idx_customers_salesperson ON customers(salesperson_id);
CREATE INDEX idx_invoices_customer ON invoices(epicor_customer_id);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_payments_customer ON payments(epicor_customer_id);
CREATE INDEX idx_alerts_customer_active ON alerts(customer_id, is_active);
CREATE INDEX idx_tasks_assigned_status ON tasks(assigned_to_user_id, status);
CREATE INDEX idx_notes_customer ON notes(customer_id);
```

### 6.2 Calculated Fields

These are computed during or after import:

```sql
-- Add to customers table or compute in views
aging_current DECIMAL(15,2),
aging_1_30 DECIMAL(15,2),
aging_31_60 DECIMAL(15,2),
aging_61_90 DECIMAL(15,2),
aging_90_plus DECIMAL(15,2),
credit_utilization_percent DECIMAL(5,2),
days_since_last_invoice INTEGER,
days_since_last_payment INTEGER,
is_inactive_flag BOOLEAN,
priority_score INTEGER
```

---

## 7. Automation & Agent System

### 7.1 Data Ingestion Agent

**Runs:** Nightly (2:00 AM) + Manual trigger option

#### Process Flow:
```
1. START Import Run
   └── Create import_runs record (status: Running)

2. FETCH Data from Epicor
   ├── Option A: Read CSVs from network folder
   ├── Option B: Execute saved Epicor reports
   └── Option C: Direct database query (read-only)

3. VALIDATE Data
   ├── Check file structure/column headers
   ├── Verify record counts within normal range
   ├── Flag missing critical fields
   └── If validation fails → Alert IT, mark failed, EXIT

4. TRANSFORM Data
   ├── Standardize formats (dates, currency)
   ├── Map Epicor codes to internal values
   └── Calculate derived fields

5. LOAD Data (Upsert)
   ├── Customers: Insert new, update existing
   ├── Invoices: Insert new, update balances
   └── Payments: Insert new, apply to invoices

6. CALCULATE
   ├── Aging buckets per customer
   ├── Credit utilization
   ├── Days since last activity
   └── Priority scores

7. GENERATE Alerts
   ├── Run all alert rules (see 7.2)
   ├── Create new alerts
   └── Resolve alerts no longer applicable

8. COMPLETE Import Run
   ├── Update import_runs with stats
   ├── Send summary email to AR Manager
   └── If errors → Include in email, log details
```

### 7.2 Alert Generation Rules

Each rule runs after every import:

#### Rule: Inactive But Owing
```python
CONDITION:
    last_invoice_date < (TODAY - 90 days)
    AND current_balance > $100  # configurable threshold
    AND status = 'Active'

ACTION:
    Create/maintain alert: type='inactive_but_owing'
    Severity:
        - > 180 days: Critical
        - > 120 days: High
        - > 90 days: Medium
```

#### Rule: Over Credit Limit
```python
CONDITION:
    current_balance > credit_limit
    AND credit_limit > 0

ACTION:
    Create alert: type='over_credit_limit'
    Severity: Critical
```

#### Rule: Near Credit Limit
```python
CONDITION:
    (current_balance / credit_limit) >= 0.80
    AND current_balance <= credit_limit
    AND credit_limit > 0

ACTION:
    Create alert: type='near_credit_limit'
    Severity: Medium
```

#### Rule: Long Overdue 60+
```python
CONDITION:
    invoice.due_date < (TODAY - 60 days)
    AND invoice.open_balance > 0

ACTION:
    Create alert: type='long_overdue_60'
    Severity: High
```

#### Rule: Long Overdue 90+
```python
CONDITION:
    invoice.due_date < (TODAY - 90 days)
    AND invoice.open_balance > 0

ACTION:
    Create alert: type='long_overdue_90'
    Severity: Critical
```

#### Rule: Broken Promise
```python
CONDITION:
    note.note_type = 'promise_to_pay'
    AND note.promise_date < TODAY
    AND note.promise_status = 'pending'
    AND related invoice still has balance

ACTION:
    Update note: promise_status = 'broken'
    Create alert: type='broken_promise'
    Severity: Critical
```

#### Rule: Unapplied Credits
```python
CONDITION:
    SUM(payments.unapplied_amount) > $500  # configurable
    OR COUNT(credit_memos with balance) > 0

ACTION:
    Create alert: type='unapplied_credits'
    Severity: Low
```

### 7.3 Scheduled Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| Data Import | 2:00 AM daily | Full sync from Epicor |
| Alert Refresh | After import | Run all alert rules |
| Priority Recalc | After alerts | Recalculate all priority scores |
| Statement Generation | 1st of month, 6:00 AM | Monthly statements |
| Past Due Statements | Weekly Monday 6:00 AM | For 30+ day accounts |
| Report Generation | 7:00 AM daily | Dashboard cache refresh |
| Broken Promise Check | 8:00 AM daily | Check promise dates |
| Reminder Emails | 9:00 AM daily | Pre-due reminders for large invoices |

---

## 8. Alert & Notification System

### 8.1 Visual Alert Hierarchy

| Severity | Color | Animation | Icon |
|----------|-------|-----------|------|
| Critical | Red (#DC2626) | Pulsing/Blinking | 🔴 |
| High | Orange (#EA580C) | Subtle pulse | 🟠 |
| Medium | Yellow (#CA8A04) | None | 🟡 |
| Low | Blue (#2563EB) | None | 🔵 |

### 8.2 Blinking/Pulsing Implementation

For CRITICAL alerts, the customer row should have visual attention:

```css
/* Critical alert row animation */
.alert-critical {
    animation: critical-pulse 1.5s ease-in-out infinite;
}

@keyframes critical-pulse {
    0%, 100% {
        background-color: #FEE2E2; /* Light red */
        border-left: 4px solid #DC2626;
    }
    50% {
        background-color: #FECACA; /* Slightly darker red */
        border-left: 4px solid #B91C1C;
    }
}

/* Alert icon pulse */
.alert-icon-critical {
    animation: icon-pulse 1s ease-in-out infinite;
}

@keyframes icon-pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.8; }
}
```

### 8.3 Alert Badge Displays

**Dashboard:**
```
┌─────────────────────────────────────┐
│ 🔴 5 Critical Alerts                │ ← Pulsing badge
│ 🟠 12 High Priority                 │
│ 🟡 23 Medium                        │
│ 🔵 8 Low                            │
└─────────────────────────────────────┘
```

**Customer Row in Worklist:**
```
│ [🔴💀] ABC Building    │ $47,500 │ $35,000 │ 95 days │ ...
           ↑
     Blinking icons: Inactive + 90+ days
```

### 8.4 Notification Channels

| Event | On-Screen | Email AR | Email Manager | Email Sales |
|-------|-----------|----------|---------------|-------------|
| New Critical Alert | Badge + Sound | Yes | Yes | If assigned |
| Import Failed | Banner | No | Yes | No |
| Promise Due Tomorrow | Task list | Yes | No | No |
| Broken Promise | Badge | Yes | Yes | If assigned |
| Over Credit Limit | Badge | Yes | Yes | Yes |
| New Dispute Logged | Badge | Yes | Yes | If assigned |

### 8.5 Daily Email Digest

**Sent to:** AR Manager + AR Specialists (6:30 AM)

```
Subject: AR Control Hub - Daily Summary for November 23, 2024

═══════════════════════════════════════════════════════════
                    OVERNIGHT CHANGES
═══════════════════════════════════════════════════════════

Data Import: ✅ Successful at 2:15 AM
  - Customers updated: 1,247
  - New invoices: 45
  - Payments applied: 23 ($67,450)

═══════════════════════════════════════════════════════════
                    TODAY'S PRIORITIES
═══════════════════════════════════════════════════════════

🔴 CRITICAL (Immediate Action Required): 5 accounts
   1. ABC Building Supply - $47,500 (Inactive 120 days)
   2. XYZ Contractors - $38,200 (Broken promise)
   3. ...

🟠 HIGH PRIORITY: 12 accounts
📋 Total accounts to contact today: 34

═══════════════════════════════════════════════════════════
                    KEY METRICS
═══════════════════════════════════════════════════════════

Total AR:        $645,000  (↑ $12,000 from yesterday)
Past Due:        $195,000  (30% of total)
90+ Days:        $45,000   (7% of total)
DSO:             38 days   (↓ 2 days from last week)

═══════════════════════════════════════════════════════════
                    PROMISES DUE TODAY
═══════════════════════════════════════════════════════════

- ABC Building: $15,000 (check supposedly mailed 11/18)
- DEF Lumber: $8,500 (ACH scheduled)

Click here to open AR Control Hub: [LINK]
```

---

## 9. UI/UX Requirements

### 9.1 Design Principles

1. **Information Density:** AR staff need lots of data visible without excessive scrolling
2. **Scannable:** Color coding, icons, and visual hierarchy for quick assessment
3. **Action-Oriented:** Common actions always 1-2 clicks away
4. **Responsive:** Works on desktop (primary) and tablet (secondary)

### 9.2 Color Palette

| Use | Color | Hex |
|-----|-------|-----|
| Primary | Blue | #2563EB |
| Success/Current | Green | #16A34A |
| Warning | Yellow | #CA8A04 |
| Danger | Red | #DC2626 |
| Neutral | Gray | #6B7280 |
| Background | Light Gray | #F9FAFB |

### 9.3 Key Screens Wireframes

See separate wireframe document: `WIREFRAMES.md`

### 9.4 Accessibility Requirements
- WCAG 2.1 AA compliance
- Keyboard navigation for all functions
- Screen reader compatible
- Color-blind friendly (patterns + colors)

---

## 10. Integration Requirements

### 10.1 Epicor Eagle Integration

**Data Flow:** Epicor → AR Control Hub (one-way, read-only)

**Methods (in order of preference):**

1. **Scheduled Report Export**
   - Configure Epicor saved reports
   - Schedule nightly export to CSV
   - AR Control Hub reads from shared folder
   - Simplest, least IT overhead

2. **Database Read (if available)**
   - Direct read-only connection to Epicor SQL database
   - Query specific tables/views
   - More real-time capable
   - Requires IT/DBA involvement

3. **API Integration (if available)**
   - Use Epicor REST API
   - Most flexible
   - Depends on Epicor version/licensing

**Required Exports:**
| Export Name | Frequency | Contents |
|-------------|-----------|----------|
| CustomerMaster.csv | Daily | All customer fields |
| OpenAR.csv | Daily | All open invoices |
| Payments.csv | Daily | Recent payments (30 days) |
| CreditStatus.csv | Daily | Hold flags, limits |

### 10.2 Email Integration

**Outbound:**
- SMTP server configuration
- Support for Office 365, Gmail, or on-premise
- HTML email templates
- Attachment capability (PDF statements)

**Tracking:**
- Delivery status webhooks (if available)
- Bounce handling
- Open tracking (optional)

### 10.3 Future Integrations (Phase 3+)

- **Customer Payment Portal:** Accept online payments
- **CRM:** Sync customer data and activities
- **Document Management:** Attach signed tickets, PODs
- **Phone System:** Click-to-call, call logging

---

## 11. Non-Functional Requirements

### 11.1 Performance

| Metric | Requirement |
|--------|-------------|
| Dashboard load | < 3 seconds |
| Worklist load | < 2 seconds |
| Customer 360 load | < 2 seconds |
| Search results | < 1 second |
| Report generation | < 30 seconds |
| Data import (full) | < 30 minutes |

### 11.2 Scalability

- Support 10,000+ customers
- Support 100,000+ open invoices
- Support 10+ concurrent users
- 3-year data retention minimum

### 11.3 Availability

- 99.5% uptime during business hours (6 AM - 8 PM local)
- Scheduled maintenance windows: Sat/Sun 2-6 AM
- Recovery time objective: 4 hours
- Recovery point objective: 24 hours (last successful import)

### 11.4 Security

| Requirement | Implementation |
|-------------|----------------|
| Authentication | SSO preferred, or username/password with MFA |
| Authorization | Role-based access control (RBAC) |
| Data encryption | TLS 1.2+ in transit, AES-256 at rest |
| Audit logging | All data access and changes logged |
| Session management | Auto-logout after 30 min inactivity |
| Password policy | Min 12 chars, complexity requirements |

### 11.5 Compliance

- PCI DSS awareness (no credit card storage)
- Data retention policies
- Right to deletion (customer data)
- Audit trail requirements

---

## 12. Phased Rollout Plan

### Phase 1: Foundation (Weeks 1-6)
**Goal:** Core functionality, prove data flow

| Week | Deliverables |
|------|--------------|
| 1-2 | Database setup, data model implementation |
| 2-3 | Epicor data export configuration, import agent |
| 3-4 | Basic dashboard, customer list view |
| 4-5 | Customer 360 view (basic), notes functionality |
| 5-6 | Testing, bug fixes, user training |

**Phase 1 Features:**
- ✅ Data import from Epicor (nightly)
- ✅ AR Dashboard with aging summary
- ✅ Customer list with basic filtering
- ✅ Customer 360 view
- ✅ Add notes and log calls
- ✅ Basic alerts (inactive, overdue)

### Phase 2: Automation (Weeks 7-12)
**Goal:** Workflow automation, communication

| Week | Deliverables |
|------|--------------|
| 7-8 | Priority scoring, worklist generation |
| 8-9 | Promise-to-pay tracking, task management |
| 9-10 | Email templates, statement generation |
| 10-11 | Advanced alerts, notification system |
| 11-12 | Salesperson view, email digests |

**Phase 2 Features:**
- ✅ Prioritized worklist with scoring
- ✅ Promise-to-pay tracking
- ✅ Broken promise detection
- ✅ Email statements and reminders
- ✅ Task management
- ✅ Salesperson portal (read-only)
- ✅ Daily email digests

### Phase 3: Analytics (Weeks 13-18)
**Goal:** Insights, forecasting, optimization

| Week | Deliverables |
|------|--------------|
| 13-14 | Cash flow forecasting |
| 14-15 | Advanced reporting, DSO analysis |
| 15-16 | Payment pattern analysis |
| 16-17 | Collections performance metrics |
| 17-18 | Dashboard refinements, user feedback |

**Phase 3 Features:**
- ✅ Cash flow forecast
- ✅ DSO trending by segment
- ✅ Collections performance dashboard
- ✅ Payment behavior scoring
- ✅ Custom report builder

### Phase 4: Advanced (Weeks 19-24)
**Goal:** Extended capabilities

- Customer payment portal
- Dispute workflow management
- CRM integration
- Mobile app
- Advanced analytics/ML

---

## 13. Success Metrics & KPIs

### 13.1 Primary KPIs

| KPI | Baseline | Target | Timeline |
|-----|----------|--------|----------|
| Days Sales Outstanding (DSO) | Measure current | -5 days | 6 months |
| % AR Current | Measure current | +15% | 6 months |
| % AR 90+ days | Measure current | -30% | 6 months |
| Collection calls/day/person | Measure current | +50% | 3 months |
| Promise-to-pay kept rate | N/A | >75% | 6 months |

### 13.2 Operational Metrics

| Metric | Target |
|--------|--------|
| Data import success rate | >99% |
| Dashboard load time | <3 sec |
| User adoption rate | >90% |
| Notes logged per collection | >95% |
| Statements sent on time | 100% |

### 13.3 Business Impact

| Metric | Measurement |
|--------|-------------|
| Cash flow improvement | Compare monthly collections pre/post |
| Bad debt reduction | Track write-offs |
| AR staff productivity | Tasks completed, calls made |
| Customer satisfaction | Dispute resolution time, complaints |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| DSO | Days Sales Outstanding - average days to collect payment |
| Aging | Categorization of AR by days past due |
| Worklist | Prioritized list of accounts/invoices requiring action |
| Promise to Pay | Customer commitment to pay by specific date |
| Credit Hold | Block on new orders due to AR issues |
| Unapplied Cash | Payments received but not applied to specific invoices |

---

## Appendix B: Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Epicor data quality issues | High | High | Data cleanup project pre-launch |
| User adoption resistance | Medium | High | Training, champion users, quick wins |
| Integration complexity | Medium | Medium | Start with CSV, evolve to API |
| Scope creep | High | Medium | Strict phase gates, change control |
| Performance with large data | Low | High | Proper indexing, query optimization |

---

## Appendix C: Open Questions

1. What is the current Epicor version and available integration methods?
2. How many active customers and open invoices currently?
3. What email system is in use (O365, Gmail, other)?
4. Are there existing AR processes documented?
5. Who are the key stakeholders for UAT?
6. What is the preferred hosting environment (cloud, on-premise)?

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Nov 2024 | AR Control Hub Team | Initial PRD |

---

*End of PRD Document*
