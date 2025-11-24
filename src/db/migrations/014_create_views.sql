-- Migration: 014_create_views
-- Description: Create views for AR Control Hub reporting and analytics
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- DATABASE VIEWS
-- Purpose: Pre-built views for common reports and dashboards
-- ============================================================================

BEGIN;

-- ============================================================================
-- AGING SUMMARY VIEW
-- Purpose: Provides aging breakdown for each customer
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_aging_summary AS
SELECT
    c.id AS customer_id,
    c.epicor_customer_id,
    c.name AS customer_name,
    c.status AS customer_status,
    c.salesperson_id,
    c.salesperson_name,
    c.branch_id,
    c.credit_limit,
    c.current_balance,
    c.credit_utilization,
    c.terms_code,
    -- Aging buckets
    COALESCE(SUM(CASE WHEN i.aging_bucket = 'Current' THEN i.open_balance ELSE 0 END), 0) AS current_amount,
    COALESCE(SUM(CASE WHEN i.aging_bucket = '1-30' THEN i.open_balance ELSE 0 END), 0) AS past_due_1_30,
    COALESCE(SUM(CASE WHEN i.aging_bucket = '31-60' THEN i.open_balance ELSE 0 END), 0) AS past_due_31_60,
    COALESCE(SUM(CASE WHEN i.aging_bucket = '61-90' THEN i.open_balance ELSE 0 END), 0) AS past_due_61_90,
    COALESCE(SUM(CASE WHEN i.aging_bucket = '90+' THEN i.open_balance ELSE 0 END), 0) AS past_due_90_plus,
    -- Totals
    COALESCE(SUM(i.open_balance), 0) AS total_open_balance,
    COALESCE(SUM(CASE WHEN i.aging_bucket != 'Current' THEN i.open_balance ELSE 0 END), 0) AS total_past_due,
    -- Invoice counts
    COUNT(CASE WHEN i.status IN ('Open', 'Partial') THEN 1 END) AS open_invoice_count,
    COUNT(CASE WHEN i.aging_bucket = '90+' THEN 1 END) AS invoices_90_plus_count,
    -- Credit memos
    COALESCE(SUM(CASE WHEN i.invoice_type = 'Credit Memo' AND i.open_balance < 0 THEN ABS(i.open_balance) ELSE 0 END), 0) AS unapplied_credits,
    -- Oldest invoice
    MIN(CASE WHEN i.status IN ('Open', 'Partial') THEN i.due_date END) AS oldest_open_due_date,
    MAX(CASE WHEN i.status IN ('Open', 'Partial') THEN i.days_past_due END) AS max_days_past_due
FROM
    customers c
    LEFT JOIN invoices i ON c.id = i.customer_id AND i.status IN ('Open', 'Partial', 'Disputed')
GROUP BY
    c.id, c.epicor_customer_id, c.name, c.status, c.salesperson_id,
    c.salesperson_name, c.branch_id, c.credit_limit, c.current_balance,
    c.credit_utilization, c.terms_code;

COMMENT ON VIEW vw_customer_aging_summary IS 'Customer aging summary with breakdown by aging bucket and totals';

-- ============================================================================
-- CUSTOMER PRIORITY SCORE VIEW
-- Purpose: Calculates a priority score for each customer based on risk factors
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_priority_score AS
SELECT
    c.id AS customer_id,
    c.epicor_customer_id,
    c.name AS customer_name,
    c.current_balance,
    c.credit_limit,
    c.credit_utilization,
    c.status AS customer_status,
    c.salesperson_name,
    c.branch_id,
    -- Component scores (higher = more attention needed)
    CASE
        WHEN c.current_balance > 100000 THEN 30
        WHEN c.current_balance > 50000 THEN 20
        WHEN c.current_balance > 25000 THEN 15
        WHEN c.current_balance > 10000 THEN 10
        ELSE 5
    END AS balance_score,
    CASE
        WHEN c.credit_utilization > 100 THEN 25
        WHEN c.credit_utilization > 90 THEN 20
        WHEN c.credit_utilization > 80 THEN 15
        WHEN c.credit_utilization > 70 THEN 10
        ELSE 0
    END AS credit_score,
    CASE
        WHEN aging.max_days_past_due > 90 THEN 30
        WHEN aging.max_days_past_due > 60 THEN 20
        WHEN aging.max_days_past_due > 30 THEN 10
        ELSE 0
    END AS aging_score,
    CASE
        WHEN aging.total_past_due > 50000 THEN 15
        WHEN aging.total_past_due > 25000 THEN 10
        WHEN aging.total_past_due > 10000 THEN 5
        ELSE 0
    END AS past_due_amount_score,
    -- Active alerts count
    COALESCE(alert_counts.critical_alerts, 0) AS critical_alerts,
    COALESCE(alert_counts.high_alerts, 0) AS high_alerts,
    COALESCE(alert_counts.total_active_alerts, 0) AS total_active_alerts,
    -- Broken promises
    COALESCE(promise_counts.broken_promises, 0) AS broken_promises_count,
    -- Calculate total priority score
    (
        CASE
            WHEN c.current_balance > 100000 THEN 30
            WHEN c.current_balance > 50000 THEN 20
            WHEN c.current_balance > 25000 THEN 15
            WHEN c.current_balance > 10000 THEN 10
            ELSE 5
        END +
        CASE
            WHEN c.credit_utilization > 100 THEN 25
            WHEN c.credit_utilization > 90 THEN 20
            WHEN c.credit_utilization > 80 THEN 15
            WHEN c.credit_utilization > 70 THEN 10
            ELSE 0
        END +
        CASE
            WHEN aging.max_days_past_due > 90 THEN 30
            WHEN aging.max_days_past_due > 60 THEN 20
            WHEN aging.max_days_past_due > 30 THEN 10
            ELSE 0
        END +
        CASE
            WHEN aging.total_past_due > 50000 THEN 15
            WHEN aging.total_past_due > 25000 THEN 10
            WHEN aging.total_past_due > 10000 THEN 5
            ELSE 0
        END +
        COALESCE(alert_counts.critical_alerts, 0) * 10 +
        COALESCE(alert_counts.high_alerts, 0) * 5 +
        COALESCE(promise_counts.broken_promises, 0) * 10
    ) AS priority_score,
    -- Priority tier
    CASE
        WHEN (
            CASE WHEN c.current_balance > 100000 THEN 30 WHEN c.current_balance > 50000 THEN 20 WHEN c.current_balance > 25000 THEN 15 WHEN c.current_balance > 10000 THEN 10 ELSE 5 END +
            CASE WHEN c.credit_utilization > 100 THEN 25 WHEN c.credit_utilization > 90 THEN 20 WHEN c.credit_utilization > 80 THEN 15 WHEN c.credit_utilization > 70 THEN 10 ELSE 0 END +
            CASE WHEN aging.max_days_past_due > 90 THEN 30 WHEN aging.max_days_past_due > 60 THEN 20 WHEN aging.max_days_past_due > 30 THEN 10 ELSE 0 END +
            CASE WHEN aging.total_past_due > 50000 THEN 15 WHEN aging.total_past_due > 25000 THEN 10 WHEN aging.total_past_due > 10000 THEN 5 ELSE 0 END +
            COALESCE(alert_counts.critical_alerts, 0) * 10 + COALESCE(alert_counts.high_alerts, 0) * 5 + COALESCE(promise_counts.broken_promises, 0) * 10
        ) >= 70 THEN 'Critical'
        WHEN (
            CASE WHEN c.current_balance > 100000 THEN 30 WHEN c.current_balance > 50000 THEN 20 WHEN c.current_balance > 25000 THEN 15 WHEN c.current_balance > 10000 THEN 10 ELSE 5 END +
            CASE WHEN c.credit_utilization > 100 THEN 25 WHEN c.credit_utilization > 90 THEN 20 WHEN c.credit_utilization > 80 THEN 15 WHEN c.credit_utilization > 70 THEN 10 ELSE 0 END +
            CASE WHEN aging.max_days_past_due > 90 THEN 30 WHEN aging.max_days_past_due > 60 THEN 20 WHEN aging.max_days_past_due > 30 THEN 10 ELSE 0 END +
            CASE WHEN aging.total_past_due > 50000 THEN 15 WHEN aging.total_past_due > 25000 THEN 10 WHEN aging.total_past_due > 10000 THEN 5 ELSE 0 END +
            COALESCE(alert_counts.critical_alerts, 0) * 10 + COALESCE(alert_counts.high_alerts, 0) * 5 + COALESCE(promise_counts.broken_promises, 0) * 10
        ) >= 50 THEN 'High'
        WHEN (
            CASE WHEN c.current_balance > 100000 THEN 30 WHEN c.current_balance > 50000 THEN 20 WHEN c.current_balance > 25000 THEN 15 WHEN c.current_balance > 10000 THEN 10 ELSE 5 END +
            CASE WHEN c.credit_utilization > 100 THEN 25 WHEN c.credit_utilization > 90 THEN 20 WHEN c.credit_utilization > 80 THEN 15 WHEN c.credit_utilization > 70 THEN 10 ELSE 0 END +
            CASE WHEN aging.max_days_past_due > 90 THEN 30 WHEN aging.max_days_past_due > 60 THEN 20 WHEN aging.max_days_past_due > 30 THEN 10 ELSE 0 END +
            CASE WHEN aging.total_past_due > 50000 THEN 15 WHEN aging.total_past_due > 25000 THEN 10 WHEN aging.total_past_due > 10000 THEN 5 ELSE 0 END +
            COALESCE(alert_counts.critical_alerts, 0) * 10 + COALESCE(alert_counts.high_alerts, 0) * 5 + COALESCE(promise_counts.broken_promises, 0) * 10
        ) >= 30 THEN 'Medium'
        ELSE 'Low'
    END AS priority_tier,
    -- Last activity dates
    c.last_invoice_date,
    c.last_payment_date,
    aging.total_past_due,
    aging.max_days_past_due
FROM
    customers c
    LEFT JOIN (
        SELECT
            customer_id,
            COALESCE(SUM(CASE WHEN aging_bucket != 'Current' THEN open_balance ELSE 0 END), 0) AS total_past_due,
            MAX(days_past_due) AS max_days_past_due
        FROM invoices
        WHERE status IN ('Open', 'Partial', 'Disputed')
        GROUP BY customer_id
    ) aging ON c.id = aging.customer_id
    LEFT JOIN (
        SELECT
            customer_id,
            COUNT(CASE WHEN severity = 'Critical' THEN 1 END) AS critical_alerts,
            COUNT(CASE WHEN severity = 'High' THEN 1 END) AS high_alerts,
            COUNT(*) AS total_active_alerts
        FROM alerts
        WHERE is_active = TRUE
        GROUP BY customer_id
    ) alert_counts ON c.id = alert_counts.customer_id
    LEFT JOIN (
        SELECT
            customer_id,
            COUNT(*) AS broken_promises
        FROM notes
        WHERE note_type = 'promise_to_pay' AND promise_status = 'broken'
        GROUP BY customer_id
    ) promise_counts ON c.id = promise_counts.customer_id
WHERE
    c.status != 'Inactive' AND c.current_balance > 0;

COMMENT ON VIEW vw_customer_priority_score IS 'Customer priority scoring for collection focus - higher score = more attention needed';

-- ============================================================================
-- AGING REPORT VIEW (COMPANY-WIDE)
-- Purpose: Company-wide aging summary for management reporting
-- ============================================================================

CREATE OR REPLACE VIEW vw_aging_report AS
SELECT
    COALESCE(c.branch_id, 'Unassigned') AS branch_id,
    COUNT(DISTINCT c.id) AS customer_count,
    COALESCE(SUM(CASE WHEN i.aging_bucket = 'Current' THEN i.open_balance ELSE 0 END), 0) AS current_amount,
    COALESCE(SUM(CASE WHEN i.aging_bucket = '1-30' THEN i.open_balance ELSE 0 END), 0) AS past_due_1_30,
    COALESCE(SUM(CASE WHEN i.aging_bucket = '31-60' THEN i.open_balance ELSE 0 END), 0) AS past_due_31_60,
    COALESCE(SUM(CASE WHEN i.aging_bucket = '61-90' THEN i.open_balance ELSE 0 END), 0) AS past_due_61_90,
    COALESCE(SUM(CASE WHEN i.aging_bucket = '90+' THEN i.open_balance ELSE 0 END), 0) AS past_due_90_plus,
    COALESCE(SUM(i.open_balance), 0) AS total_ar,
    COUNT(DISTINCT i.id) AS invoice_count
FROM
    customers c
    LEFT JOIN invoices i ON c.id = i.customer_id AND i.status IN ('Open', 'Partial', 'Disputed')
WHERE
    c.status != 'Inactive'
GROUP BY
    c.branch_id
ORDER BY
    total_ar DESC;

COMMENT ON VIEW vw_aging_report IS 'Company-wide aging summary grouped by branch';

-- ============================================================================
-- OPEN TASKS VIEW
-- Purpose: Lists all open tasks with customer and user details
-- ============================================================================

CREATE OR REPLACE VIEW vw_open_tasks AS
SELECT
    t.id AS task_id,
    t.task_type,
    t.description,
    t.due_at,
    t.status,
    t.priority,
    c.id AS customer_id,
    c.epicor_customer_id,
    c.name AS customer_name,
    c.current_balance AS customer_balance,
    u.id AS assigned_user_id,
    u.full_name AS assigned_to_name,
    u.email AS assigned_to_email,
    i.epicor_invoice_number,
    i.open_balance AS invoice_balance,
    CASE
        WHEN t.due_at < CURRENT_TIMESTAMP THEN 'Overdue'
        WHEN t.due_at < CURRENT_TIMESTAMP + INTERVAL '1 day' THEN 'Due Today'
        WHEN t.due_at < CURRENT_TIMESTAMP + INTERVAL '7 days' THEN 'Due This Week'
        ELSE 'Future'
    END AS urgency,
    t.created_at
FROM
    tasks t
    INNER JOIN customers c ON t.customer_id = c.id
    INNER JOIN users u ON t.assigned_to_user_id = u.id
    LEFT JOIN invoices i ON t.invoice_id = i.id
WHERE
    t.status IN ('Open', 'In Progress')
ORDER BY
    t.priority ASC, t.due_at ASC;

COMMENT ON VIEW vw_open_tasks IS 'All open tasks with customer and assigned user details';

-- ============================================================================
-- ACTIVE ALERTS VIEW
-- Purpose: Lists all active alerts with customer details
-- ============================================================================

CREATE OR REPLACE VIEW vw_active_alerts AS
SELECT
    a.id AS alert_id,
    a.alert_type,
    a.severity,
    a.title,
    a.message,
    a.triggered_at,
    c.id AS customer_id,
    c.epicor_customer_id,
    c.name AS customer_name,
    c.current_balance,
    c.credit_limit,
    c.status AS customer_status,
    i.epicor_invoice_number,
    i.open_balance AS invoice_balance,
    i.days_past_due,
    CASE a.severity
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        ELSE 4
    END AS severity_order
FROM
    alerts a
    INNER JOIN customers c ON a.customer_id = c.id
    LEFT JOIN invoices i ON a.invoice_id = i.id
WHERE
    a.is_active = TRUE
ORDER BY
    severity_order ASC, a.triggered_at DESC;

COMMENT ON VIEW vw_active_alerts IS 'All active alerts with customer and invoice details, sorted by severity';

-- ============================================================================
-- PROMISE TO PAY TRACKING VIEW
-- Purpose: Tracks all promise-to-pay commitments
-- ============================================================================

CREATE OR REPLACE VIEW vw_promise_to_pay AS
SELECT
    n.id AS note_id,
    n.promise_amount,
    n.promise_date,
    n.promise_status,
    n.content AS notes,
    n.created_at,
    c.id AS customer_id,
    c.epicor_customer_id,
    c.name AS customer_name,
    c.current_balance,
    u.full_name AS created_by,
    CASE
        WHEN n.promise_status = 'pending' AND n.promise_date < CURRENT_DATE THEN 'Overdue'
        WHEN n.promise_status = 'pending' AND n.promise_date = CURRENT_DATE THEN 'Due Today'
        WHEN n.promise_status = 'pending' THEN 'Upcoming'
        ELSE n.promise_status
    END AS promise_state
FROM
    notes n
    INNER JOIN customers c ON n.customer_id = c.id
    INNER JOIN users u ON n.user_id = u.id
WHERE
    n.note_type = 'promise_to_pay'
ORDER BY
    CASE n.promise_status WHEN 'pending' THEN 0 ELSE 1 END,
    n.promise_date ASC;

COMMENT ON VIEW vw_promise_to_pay IS 'All promise-to-pay commitments with status tracking';

-- ============================================================================
-- COLLECTION ACTIVITY SUMMARY VIEW
-- Purpose: Daily/weekly collection activity metrics
-- ============================================================================

CREATE OR REPLACE VIEW vw_collection_activity_summary AS
SELECT
    DATE(n.created_at) AS activity_date,
    u.id AS user_id,
    u.full_name AS user_name,
    COUNT(CASE WHEN n.note_type = 'call' THEN 1 END) AS calls_made,
    COUNT(CASE WHEN n.note_type = 'email' THEN 1 END) AS emails_sent,
    COUNT(CASE WHEN n.note_type = 'promise_to_pay' THEN 1 END) AS promises_obtained,
    SUM(CASE WHEN n.note_type = 'promise_to_pay' THEN n.promise_amount ELSE 0 END) AS total_promised_amount,
    COUNT(DISTINCT n.customer_id) AS customers_contacted
FROM
    notes n
    INNER JOIN users u ON n.user_id = u.id
WHERE
    n.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY
    DATE(n.created_at), u.id, u.full_name
ORDER BY
    activity_date DESC, user_name;

COMMENT ON VIEW vw_collection_activity_summary IS 'Daily collection activity metrics by user for the last 30 days';

-- ============================================================================
-- UNAPPLIED PAYMENTS VIEW
-- Purpose: Lists payments with unapplied amounts
-- ============================================================================

CREATE OR REPLACE VIEW vw_unapplied_payments AS
SELECT
    p.id AS payment_id,
    p.epicor_payment_id,
    p.payment_date,
    p.amount AS total_amount,
    p.unapplied_amount,
    p.payment_type,
    p.check_number,
    p.reference_number,
    c.id AS customer_id,
    c.epicor_customer_id,
    c.name AS customer_name,
    c.current_balance,
    ROUND((p.unapplied_amount / p.amount * 100)::numeric, 2) AS unapplied_percentage
FROM
    payments p
    INNER JOIN customers c ON p.customer_id = c.id
WHERE
    p.unapplied_amount > 0
ORDER BY
    p.unapplied_amount DESC;

COMMENT ON VIEW vw_unapplied_payments IS 'Payments with unapplied balances that need attention';

-- ============================================================================
-- DASHBOARD SUMMARY VIEW
-- Purpose: High-level metrics for dashboard
-- ============================================================================

CREATE OR REPLACE VIEW vw_dashboard_summary AS
SELECT
    -- AR Totals
    (SELECT COALESCE(SUM(current_balance), 0) FROM customers WHERE status != 'Inactive') AS total_ar_balance,
    (SELECT COUNT(*) FROM customers WHERE status != 'Inactive' AND current_balance > 0) AS customers_with_balance,

    -- Aging totals
    (SELECT COALESCE(SUM(open_balance), 0) FROM invoices WHERE status IN ('Open', 'Partial') AND aging_bucket = 'Current') AS current_amount,
    (SELECT COALESCE(SUM(open_balance), 0) FROM invoices WHERE status IN ('Open', 'Partial') AND aging_bucket != 'Current') AS past_due_amount,
    (SELECT COALESCE(SUM(open_balance), 0) FROM invoices WHERE status IN ('Open', 'Partial') AND aging_bucket = '90+') AS over_90_amount,

    -- Invoice counts
    (SELECT COUNT(*) FROM invoices WHERE status IN ('Open', 'Partial')) AS open_invoice_count,
    (SELECT COUNT(*) FROM invoices WHERE status = 'Disputed') AS disputed_invoice_count,

    -- Alert counts
    (SELECT COUNT(*) FROM alerts WHERE is_active = TRUE) AS active_alert_count,
    (SELECT COUNT(*) FROM alerts WHERE is_active = TRUE AND severity = 'Critical') AS critical_alert_count,

    -- Task counts
    (SELECT COUNT(*) FROM tasks WHERE status IN ('Open', 'In Progress')) AS open_task_count,
    (SELECT COUNT(*) FROM tasks WHERE status IN ('Open', 'In Progress') AND due_at < CURRENT_TIMESTAMP) AS overdue_task_count,

    -- Promise tracking
    (SELECT COUNT(*) FROM notes WHERE note_type = 'promise_to_pay' AND promise_status = 'pending') AS pending_promises,
    (SELECT COALESCE(SUM(promise_amount), 0) FROM notes WHERE note_type = 'promise_to_pay' AND promise_status = 'pending') AS total_promised_amount,

    -- Credit holds
    (SELECT COUNT(*) FROM credit_holds WHERE is_active = TRUE) AS customers_on_hold,

    -- Disputes
    (SELECT COUNT(*) FROM disputes WHERE status NOT IN ('Resolved', 'Rejected')) AS open_dispute_count,
    (SELECT COALESCE(SUM(disputed_amount), 0) FROM disputes WHERE status NOT IN ('Resolved', 'Rejected')) AS total_disputed_amount;

COMMENT ON VIEW vw_dashboard_summary IS 'High-level AR metrics for dashboard display';

COMMIT;
