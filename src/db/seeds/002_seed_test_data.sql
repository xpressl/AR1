-- Seed: 002_seed_test_data
-- Description: Seed test data for AR Control Hub development and testing
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- SEED TEST DATA
-- Purpose: Create sample customers, invoices, payments, and related records
-- Note: This data is for development/testing only
-- ============================================================================

BEGIN;

-- ============================================================================
-- CUSTOMERS
-- ============================================================================

INSERT INTO customers (
    epicor_customer_id, name, dba_trade_name,
    billing_address_line1, billing_city, billing_state, billing_zip,
    billing_email, billing_phone, primary_contact_name,
    salesperson_id, salesperson_name, terms_code,
    credit_limit, current_balance, status, customer_type, branch_id
) VALUES
    -- Active customers with balances
    ('CUST001', 'Acme Manufacturing Inc', 'Acme Mfg',
     '123 Industrial Way', 'Chicago', 'IL', '60601',
     'ap@acmemfg.com', '312-555-0100', 'John Smith',
     'SR001', 'David Brown', 'NET30',
     100000.00, 45750.00, 'Active', 'Industrial', 'MAIN'),

    ('CUST002', 'TechCorp Solutions LLC', NULL,
     '456 Tech Park Drive', 'San Francisco', 'CA', '94102',
     'accounts@techcorp.com', '415-555-0200', 'Maria Garcia',
     'SR001', 'David Brown', 'NET30',
     75000.00, 62500.00, 'Active', 'Technology', 'WEST'),

    ('CUST003', 'BuildRight Construction', 'BuildRight',
     '789 Builder Lane', 'Denver', 'CO', '80201',
     'billing@buildright.com', '303-555-0300', 'Tom Johnson',
     'SR002', 'Emily Martinez', 'NET45',
     150000.00, 128000.00, 'Active', 'Construction', 'WEST'),

    ('CUST004', 'Global Distributors Inc', NULL,
     '321 Commerce Street', 'Dallas', 'TX', '75201',
     'ar@globaldist.com', '214-555-0400', 'Sarah Williams',
     'SR001', 'David Brown', 'NET60',
     200000.00, 85000.00, 'Active', 'Distribution', 'MAIN'),

    ('CUST005', 'Metro Healthcare Systems', 'Metro Health',
     '555 Medical Center Blvd', 'Boston', 'MA', '02101',
     'finance@metrohealth.org', '617-555-0500', 'Dr. James Lee',
     'SR002', 'Emily Martinez', 'NET30',
     250000.00, 175000.00, 'Active', 'Healthcare', 'MAIN'),

    -- Customer on credit hold
    ('CUST006', 'Struggling Supplies Co', NULL,
     '999 Hard Times Ave', 'Detroit', 'MI', '48201',
     'ap@struggling.com', '313-555-0600', 'Mike Peters',
     'SR001', 'David Brown', 'COD',
     25000.00, 32000.00, 'On Hold', 'Retail', 'MAIN'),

    -- Customer with large past due
    ('CUST007', 'DeepPockets Enterprises', 'DeepPockets',
     '777 Wealth Way', 'New York', 'NY', '10001',
     'accounts@deeppockets.com', '212-555-0700', 'Richard Gold',
     'SR002', 'Emily Martinez', 'NET30',
     500000.00, 425000.00, 'Active', 'Investment', 'MAIN'),

    -- Small customer with clean record
    ('CUST008', 'Local Shop LLC', 'The Local Shop',
     '100 Main Street', 'Austin', 'TX', '78701',
     'owner@localshop.com', '512-555-0800', 'Jane Doe',
     'SR001', 'David Brown', 'NET30',
     10000.00, 2500.00, 'Active', 'Retail', 'WEST'),

    -- Inactive customer with balance
    ('CUST009', 'Defunct Industries', NULL,
     '000 Closed Road', 'Phoenix', 'AZ', '85001',
     'none@defunct.com', '602-555-0900', 'Unknown',
     'SR001', 'David Brown', 'NET30',
     50000.00, 15000.00, 'Inactive', 'Manufacturing', 'MAIN'),

    -- COD customer
    ('CUST010', 'Cash Only Services', NULL,
     '222 Pay Now Lane', 'Seattle', 'WA', '98101',
     'billing@cashonly.com', '206-555-1000', 'Peter Cash',
     'SR002', 'Emily Martinez', 'COD',
     0.00, 0.00, 'COD', 'Services', 'WEST')

ON CONFLICT (epicor_customer_id) DO NOTHING;

-- Update last invoice/payment dates
UPDATE customers SET
    last_invoice_date = CURRENT_DATE - INTERVAL '15 days',
    last_payment_date = CURRENT_DATE - INTERVAL '30 days'
WHERE epicor_customer_id = 'CUST001';

UPDATE customers SET
    last_invoice_date = CURRENT_DATE - INTERVAL '45 days',
    last_payment_date = CURRENT_DATE - INTERVAL '60 days'
WHERE epicor_customer_id = 'CUST002';

UPDATE customers SET
    last_invoice_date = CURRENT_DATE - INTERVAL '5 days',
    last_payment_date = CURRENT_DATE - INTERVAL '20 days'
WHERE epicor_customer_id = 'CUST003';

UPDATE customers SET
    last_invoice_date = CURRENT_DATE - INTERVAL '90 days',
    last_payment_date = CURRENT_DATE - INTERVAL '120 days'
WHERE epicor_customer_id = 'CUST009';

-- ============================================================================
-- INVOICES
-- ============================================================================

-- CUST001 - Acme Manufacturing (Current and slightly past due)
INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id, po_reference
)
SELECT
    'INV-2025-0001', c.id, CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE + INTERVAL '15 days',
    15000.00, 15000.00, 'Open', 'Invoice', 'MAIN', 'SR001', 'PO-ACM-001'
FROM customers c WHERE c.epicor_customer_id = 'CUST001';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id, po_reference
)
SELECT
    'INV-2025-0002', c.id, CURRENT_DATE - INTERVAL '45 days', CURRENT_DATE - INTERVAL '15 days',
    20000.00, 20000.00, 'Open', 'Invoice', 'MAIN', 'SR001', 'PO-ACM-002'
FROM customers c WHERE c.epicor_customer_id = 'CUST001';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id, po_reference
)
SELECT
    'INV-2025-0003', c.id, CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '30 days',
    10750.00, 10750.00, 'Open', 'Invoice', 'MAIN', 'SR001', 'PO-ACM-003'
FROM customers c WHERE c.epicor_customer_id = 'CUST001';

-- CUST002 - TechCorp (Over credit limit, past due)
INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0004', c.id, CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE - INTERVAL '60 days',
    35000.00, 35000.00, 'Open', 'Invoice', 'WEST', 'SR001'
FROM customers c WHERE c.epicor_customer_id = 'CUST002';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0005', c.id, CURRENT_DATE - INTERVAL '45 days', CURRENT_DATE - INTERVAL '15 days',
    27500.00, 27500.00, 'Open', 'Invoice', 'WEST', 'SR001'
FROM customers c WHERE c.epicor_customer_id = 'CUST002';

-- CUST003 - BuildRight (Large balance, various aging)
INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id, job_reference
)
SELECT
    'INV-2025-0006', c.id, CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE + INTERVAL '40 days',
    45000.00, 45000.00, 'Open', 'Invoice', 'WEST', 'SR002', 'JOB-BR-100'
FROM customers c WHERE c.epicor_customer_id = 'CUST003';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id, job_reference
)
SELECT
    'INV-2025-0007', c.id, CURRENT_DATE - INTERVAL '75 days', CURRENT_DATE - INTERVAL '30 days',
    55000.00, 55000.00, 'Open', 'Invoice', 'WEST', 'SR002', 'JOB-BR-099'
FROM customers c WHERE c.epicor_customer_id = 'CUST003';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id, job_reference
)
SELECT
    'INV-2025-0008', c.id, CURRENT_DATE - INTERVAL '120 days', CURRENT_DATE - INTERVAL '75 days',
    28000.00, 28000.00, 'Open', 'Invoice', 'WEST', 'SR002', 'JOB-BR-098'
FROM customers c WHERE c.epicor_customer_id = 'CUST003';

-- CUST005 - Metro Healthcare (Large balances, some disputed)
INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0009', c.id, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '20 days',
    75000.00, 75000.00, 'Open', 'Invoice', 'MAIN', 'SR002'
FROM customers c WHERE c.epicor_customer_id = 'CUST005';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0010', c.id, CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '30 days',
    50000.00, 50000.00, 'Disputed', 'Invoice', 'MAIN', 'SR002'
FROM customers c WHERE c.epicor_customer_id = 'CUST005';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0011', c.id, CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE - INTERVAL '60 days',
    50000.00, 50000.00, 'Open', 'Invoice', 'MAIN', 'SR002'
FROM customers c WHERE c.epicor_customer_id = 'CUST005';

-- CUST006 - Struggling Supplies (On hold, severely past due)
INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0012', c.id, CURRENT_DATE - INTERVAL '150 days', CURRENT_DATE - INTERVAL '120 days',
    18000.00, 18000.00, 'Open', 'Invoice', 'MAIN', 'SR001'
FROM customers c WHERE c.epicor_customer_id = 'CUST006';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0013', c.id, CURRENT_DATE - INTERVAL '120 days', CURRENT_DATE - INTERVAL '90 days',
    14000.00, 14000.00, 'Open', 'Invoice', 'MAIN', 'SR001'
FROM customers c WHERE c.epicor_customer_id = 'CUST006';

-- CUST007 - DeepPockets (Large balances across all aging buckets)
INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0014', c.id, CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE + INTERVAL '25 days',
    125000.00, 125000.00, 'Open', 'Invoice', 'MAIN', 'SR002'
FROM customers c WHERE c.epicor_customer_id = 'CUST007';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0015', c.id, CURRENT_DATE - INTERVAL '45 days', CURRENT_DATE - INTERVAL '15 days',
    100000.00, 100000.00, 'Open', 'Invoice', 'MAIN', 'SR002'
FROM customers c WHERE c.epicor_customer_id = 'CUST007';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0016', c.id, CURRENT_DATE - INTERVAL '75 days', CURRENT_DATE - INTERVAL '45 days',
    100000.00, 100000.00, 'Open', 'Invoice', 'MAIN', 'SR002'
FROM customers c WHERE c.epicor_customer_id = 'CUST007';

INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0017', c.id, CURRENT_DATE - INTERVAL '120 days', CURRENT_DATE - INTERVAL '90 days',
    100000.00, 100000.00, 'Open', 'Invoice', 'MAIN', 'SR002'
FROM customers c WHERE c.epicor_customer_id = 'CUST007';

-- CUST008 - Local Shop (Small, current)
INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'INV-2025-0018', c.id, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '20 days',
    2500.00, 2500.00, 'Open', 'Invoice', 'WEST', 'SR001'
FROM customers c WHERE c.epicor_customer_id = 'CUST008';

-- Credit Memo for CUST001
INSERT INTO invoices (
    epicor_invoice_number, customer_id, invoice_date, due_date,
    original_amount, open_balance, status, invoice_type,
    branch_id, salesperson_id
)
SELECT
    'CM-2025-0001', c.id, CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE - INTERVAL '20 days',
    -500.00, -500.00, 'Open', 'Credit Memo', 'MAIN', 'SR001'
FROM customers c WHERE c.epicor_customer_id = 'CUST001';

-- ============================================================================
-- PAYMENTS
-- ============================================================================

-- Payment for CUST001
INSERT INTO payments (
    epicor_payment_id, customer_id, payment_date, amount,
    payment_type, check_number, unapplied_amount
)
SELECT
    'PAY-2025-0001', c.id, CURRENT_DATE - INTERVAL '30 days', 25000.00,
    'Check', '12345', 0.00
FROM customers c WHERE c.epicor_customer_id = 'CUST001';

-- Payment for CUST003
INSERT INTO payments (
    epicor_payment_id, customer_id, payment_date, amount,
    payment_type, reference_number, unapplied_amount
)
SELECT
    'PAY-2025-0002', c.id, CURRENT_DATE - INTERVAL '20 days', 50000.00,
    'ACH', 'ACH-789456', 0.00
FROM customers c WHERE c.epicor_customer_id = 'CUST003';

-- Payment for CUST007 with unapplied amount
INSERT INTO payments (
    epicor_payment_id, customer_id, payment_date, amount,
    payment_type, reference_number, unapplied_amount
)
SELECT
    'PAY-2025-0003', c.id, CURRENT_DATE - INTERVAL '15 days', 100000.00,
    'Wire', 'WIRE-123456', 25000.00
FROM customers c WHERE c.epicor_customer_id = 'CUST007';

-- ============================================================================
-- DISPUTES
-- ============================================================================

-- Dispute for CUST005 invoice
INSERT INTO disputes (
    customer_id, invoice_id, assigned_to_user_id, created_by_user_id,
    reason_code, description, disputed_amount, status, priority
)
SELECT
    c.id,
    i.id,
    u.id,
    u.id,
    'pricing',
    'Customer claims pricing does not match contract rates. Reviewing contract terms.',
    50000.00,
    'In Review',
    3
FROM customers c
JOIN invoices i ON c.id = i.customer_id AND i.epicor_invoice_number = 'INV-2025-0010'
JOIN users u ON u.username = 'ar_specialist1'
WHERE c.epicor_customer_id = 'CUST005';

-- ============================================================================
-- ALERTS
-- ============================================================================

-- Over credit limit alert for CUST002
INSERT INTO alerts (
    customer_id, alert_type, severity, title, message, is_active
)
SELECT
    c.id,
    'over_credit_limit',
    'High',
    'Customer Over Credit Limit',
    'TechCorp Solutions LLC is $12,500 over their $75,000 credit limit. Current balance: $87,500.',
    TRUE
FROM customers c WHERE c.epicor_customer_id = 'CUST002';

-- Long overdue alert for CUST006
INSERT INTO alerts (
    customer_id, alert_type, severity, title, message, is_active
)
SELECT
    c.id,
    'long_overdue_90',
    'Critical',
    'Invoices Over 90 Days Past Due',
    'Struggling Supplies Co has $32,000 in invoices over 90 days past due.',
    TRUE
FROM customers c WHERE c.epicor_customer_id = 'CUST006';

-- Inactive but owing alert for CUST009
INSERT INTO alerts (
    customer_id, alert_type, severity, title, message, is_active
)
SELECT
    c.id,
    'inactive_but_owing',
    'Medium',
    'Inactive Customer With Balance',
    'Defunct Industries is marked inactive but has an outstanding balance of $15,000.',
    TRUE
FROM customers c WHERE c.epicor_customer_id = 'CUST009';

-- ============================================================================
-- NOTES
-- ============================================================================

-- Collection call note for CUST002
INSERT INTO notes (
    customer_id, user_id, note_type, content,
    contact_name, contact_phone
)
SELECT
    c.id,
    u.id,
    'call',
    'Called Maria Garcia regarding past due invoices. She stated payment is being processed and should be sent by end of week. Will follow up if payment not received.',
    'Maria Garcia',
    '415-555-0200'
FROM customers c
JOIN users u ON u.username = 'ar_specialist1'
WHERE c.epicor_customer_id = 'CUST002';

-- Promise to pay note for CUST006
INSERT INTO notes (
    customer_id, user_id, note_type, content,
    promise_amount, promise_date, promise_status,
    contact_name, contact_phone
)
SELECT
    c.id,
    u.id,
    'promise_to_pay',
    'Mike Peters promised to pay $10,000 towards the oldest invoice. Company is having cash flow issues but committed to paying down balance.',
    10000.00,
    CURRENT_DATE + INTERVAL '7 days',
    'pending',
    'Mike Peters',
    '313-555-0600'
FROM customers c
JOIN users u ON u.username = 'ar_specialist1'
WHERE c.epicor_customer_id = 'CUST006';

-- Broken promise note for CUST006 (historical)
INSERT INTO notes (
    customer_id, user_id, note_type, content,
    promise_amount, promise_date, promise_status,
    contact_name, created_at
)
SELECT
    c.id,
    u.id,
    'promise_to_pay',
    'Customer promised $15,000 payment that was never received. Multiple follow-up calls went to voicemail.',
    15000.00,
    CURRENT_DATE - INTERVAL '30 days',
    'broken',
    'Mike Peters',
    CURRENT_DATE - INTERVAL '45 days'
FROM customers c
JOIN users u ON u.username = 'ar_specialist2'
WHERE c.epicor_customer_id = 'CUST006';

-- ============================================================================
-- TASKS
-- ============================================================================

-- Follow up task for CUST002
INSERT INTO tasks (
    customer_id, assigned_to_user_id, created_by_user_id,
    task_type, description, due_at, status, priority
)
SELECT
    c.id,
    u.id,
    u.id,
    'follow_up',
    'Follow up on payment promise. Maria Garcia stated payment would be sent by end of week.',
    CURRENT_DATE + INTERVAL '3 days',
    'Open',
    3
FROM customers c
JOIN users u ON u.username = 'ar_specialist1'
WHERE c.epicor_customer_id = 'CUST002';

-- Collection call task for CUST006
INSERT INTO tasks (
    customer_id, assigned_to_user_id, created_by_user_id,
    task_type, description, due_at, status, priority
)
SELECT
    c.id,
    u.id,
    u.id,
    'collection_call',
    'Escalated collection call needed. Customer has broken previous promise and account is severely past due.',
    CURRENT_DATE,
    'Open',
    1
FROM customers c
JOIN users u ON u.username = 'ar_specialist1'
WHERE c.epicor_customer_id = 'CUST006';

-- Review task for CUST007
INSERT INTO tasks (
    customer_id, assigned_to_user_id, created_by_user_id,
    task_type, description, due_at, status, priority
)
SELECT
    c.id,
    u.id,
    m.id,
    'review',
    'Review account - large balance with $25,000 unapplied payment. Determine where to apply credits.',
    CURRENT_DATE + INTERVAL '1 day',
    'Open',
    2
FROM customers c
JOIN users u ON u.username = 'ar_specialist2'
JOIN users m ON m.username = 'ar_manager'
WHERE c.epicor_customer_id = 'CUST007';

-- Send statement task for CUST003
INSERT INTO tasks (
    customer_id, assigned_to_user_id, created_by_user_id,
    task_type, description, due_at, status, priority
)
SELECT
    c.id,
    u.id,
    u.id,
    'send_statement',
    'Send monthly statement to BuildRight Construction. Include aging summary.',
    CURRENT_DATE + INTERVAL '2 days',
    'Open',
    5
FROM customers c
JOIN users u ON u.username = 'ar_specialist3'
WHERE c.epicor_customer_id = 'CUST003';

-- ============================================================================
-- CREDIT HOLDS
-- ============================================================================

-- Active credit hold for CUST006
INSERT INTO credit_holds (
    customer_id, placed_by_user_id, reason_code, reason_note,
    balance_at_hold, credit_limit_at_hold, oldest_invoice_days
)
SELECT
    c.id,
    u.id,
    'past_due',
    'Account severely past due with over $30,000 in invoices over 90 days. Multiple broken payment promises.',
    32000.00,
    25000.00,
    120
FROM customers c
JOIN users u ON u.username = 'ar_manager'
WHERE c.epicor_customer_id = 'CUST006';

-- ============================================================================
-- EMAIL LOG
-- ============================================================================

-- Statement email for CUST001
INSERT INTO email_log (
    customer_id, sent_by_user_id, email_type, template_used,
    recipient_email, recipient_name, subject, delivery_status
)
SELECT
    c.id,
    u.id,
    'statement',
    'monthly_statement',
    'ap@acmemfg.com',
    'John Smith',
    'Your Monthly Statement from Company - January 2025',
    'delivered'
FROM customers c
JOIN users u ON u.username = 'ar_specialist1'
WHERE c.epicor_customer_id = 'CUST001';

-- Past due notice for CUST002
INSERT INTO email_log (
    customer_id, sent_by_user_id, email_type, template_used,
    recipient_email, recipient_name, subject, delivery_status
)
SELECT
    c.id,
    u.id,
    'past_due_notice',
    'past_due_30',
    'accounts@techcorp.com',
    'Maria Garcia',
    'Past Due Notice - Immediate Attention Required',
    'opened'
FROM customers c
JOIN users u ON u.username = 'ar_specialist1'
WHERE c.epicor_customer_id = 'CUST002';

-- ============================================================================
-- IMPORT RUNS
-- ============================================================================

-- Record of last successful import
INSERT INTO import_runs (
    import_type, started_at, finished_at, status,
    customers_processed, customers_imported, customers_updated,
    invoices_processed, invoices_imported, invoices_updated,
    payments_processed, payments_imported,
    alerts_generated, alerts_resolved,
    trigger_type
) VALUES (
    'incremental',
    CURRENT_TIMESTAMP - INTERVAL '2 hours',
    CURRENT_TIMESTAMP - INTERVAL '1 hour 55 minutes',
    'Success',
    10, 0, 10,
    18, 2, 16,
    3, 1,
    3, 1,
    'scheduled'
);

-- ============================================================================
-- OUTPUT SUMMARY
-- ============================================================================

DO $$
DECLARE
    customer_count INTEGER;
    invoice_count INTEGER;
    payment_count INTEGER;
    task_count INTEGER;
    alert_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO customer_count FROM customers;
    SELECT COUNT(*) INTO invoice_count FROM invoices;
    SELECT COUNT(*) INTO payment_count FROM payments;
    SELECT COUNT(*) INTO task_count FROM tasks;
    SELECT COUNT(*) INTO alert_count FROM alerts;

    RAISE NOTICE 'Test data seeded successfully:';
    RAISE NOTICE '  - Customers: %', customer_count;
    RAISE NOTICE '  - Invoices: %', invoice_count;
    RAISE NOTICE '  - Payments: %', payment_count;
    RAISE NOTICE '  - Tasks: %', task_count;
    RAISE NOTICE '  - Alerts: %', alert_count;
END $$;

COMMIT;
