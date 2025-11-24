-- Migration: 013_create_indexes
-- Description: Create additional indexes for AR Control Hub performance optimization
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- PERFORMANCE INDEXES
-- Purpose: Create indexes for frequently used queries and reports
-- ============================================================================

BEGIN;

-- ============================================================================
-- CUSTOMERS TABLE INDEXES
-- ============================================================================

-- Status filtering (common in list views)
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);

-- Salesperson assignment (for sales rep filtered views)
CREATE INDEX IF NOT EXISTS idx_customers_salesperson_id ON customers(salesperson_id);

-- Branch filtering
CREATE INDEX IF NOT EXISTS idx_customers_branch_id ON customers(branch_id);

-- Last invoice date (for inactive customer alerts)
CREATE INDEX IF NOT EXISTS idx_customers_last_invoice_date ON customers(last_invoice_date);

-- Last payment date (for payment history)
CREATE INDEX IF NOT EXISTS idx_customers_last_payment_date ON customers(last_payment_date);

-- Credit utilization (for credit risk queries)
CREATE INDEX IF NOT EXISTS idx_customers_credit_utilization ON customers(credit_utilization);

-- Current balance (for high balance queries)
CREATE INDEX IF NOT EXISTS idx_customers_current_balance ON customers(current_balance DESC);

-- Composite index for common filters
CREATE INDEX IF NOT EXISTS idx_customers_status_branch ON customers(status, branch_id);
CREATE INDEX IF NOT EXISTS idx_customers_status_salesperson ON customers(status, salesperson_id);

-- Full text search on customer name
CREATE INDEX IF NOT EXISTS idx_customers_name_trgm ON customers USING gin (name gin_trgm_ops);

-- ============================================================================
-- INVOICES TABLE INDEXES
-- ============================================================================

-- Customer ID (foreign key, already created but ensuring optimization)
CREATE INDEX IF NOT EXISTS idx_invoices_customer_id_status ON invoices(customer_id, status);

-- Due date (for aging reports and overdue queries)
CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON invoices(due_date);

-- Status filtering
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);

-- Aging bucket (for aging reports)
CREATE INDEX IF NOT EXISTS idx_invoices_aging_bucket ON invoices(aging_bucket);

-- Days past due (for overdue filtering)
CREATE INDEX IF NOT EXISTS idx_invoices_days_past_due ON invoices(days_past_due DESC);

-- Invoice date (for date range queries)
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_date ON invoices(invoice_date);

-- Open balance (for largest balance queries)
CREATE INDEX IF NOT EXISTS idx_invoices_open_balance ON invoices(open_balance DESC) WHERE open_balance > 0;

-- Branch and department filtering
CREATE INDEX IF NOT EXISTS idx_invoices_branch_id ON invoices(branch_id);
CREATE INDEX IF NOT EXISTS idx_invoices_department ON invoices(department);
CREATE INDEX IF NOT EXISTS idx_invoices_salesperson_id ON invoices(salesperson_id);

-- Invoice type
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_type ON invoices(invoice_type);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_invoices_customer_status_due ON invoices(customer_id, status, due_date);
CREATE INDEX IF NOT EXISTS idx_invoices_status_aging ON invoices(status, aging_bucket) WHERE status = 'Open';
CREATE INDEX IF NOT EXISTS idx_invoices_open_by_customer ON invoices(customer_id, open_balance) WHERE status IN ('Open', 'Partial');

-- Reference number searches
CREATE INDEX IF NOT EXISTS idx_invoices_po_reference ON invoices(po_reference) WHERE po_reference IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_invoices_order_number ON invoices(order_number) WHERE order_number IS NOT NULL;

-- ============================================================================
-- PAYMENTS TABLE INDEXES
-- ============================================================================

-- Customer ID (for payment history)
CREATE INDEX IF NOT EXISTS idx_payments_customer_id_date ON payments(customer_id, payment_date DESC);

-- Payment date (for date range queries)
CREATE INDEX IF NOT EXISTS idx_payments_payment_date ON payments(payment_date DESC);

-- Payment type
CREATE INDEX IF NOT EXISTS idx_payments_payment_type ON payments(payment_type);

-- Unapplied amounts (for unapplied payment queries)
CREATE INDEX IF NOT EXISTS idx_payments_unapplied ON payments(unapplied_amount) WHERE unapplied_amount > 0;

-- Check number lookup
CREATE INDEX IF NOT EXISTS idx_payments_check_number ON payments(check_number) WHERE check_number IS NOT NULL;

-- ============================================================================
-- ALERTS TABLE INDEXES
-- ============================================================================

-- Customer ID with active status
CREATE INDEX IF NOT EXISTS idx_alerts_customer_active ON alerts(customer_id, is_active) WHERE is_active = TRUE;

-- Active alerts by type
CREATE INDEX IF NOT EXISTS idx_alerts_is_active ON alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_active_type ON alerts(alert_type, severity) WHERE is_active = TRUE;

-- Alert type
CREATE INDEX IF NOT EXISTS idx_alerts_alert_type ON alerts(alert_type);

-- Severity for priority sorting
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity) WHERE is_active = TRUE;

-- Triggered at (for recent alerts)
CREATE INDEX IF NOT EXISTS idx_alerts_triggered_at ON alerts(triggered_at DESC);

-- ============================================================================
-- TASKS TABLE INDEXES
-- ============================================================================

-- Assigned user with status
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_status ON tasks(assigned_to_user_id, status);

-- Status and due date (for task list views)
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_at ON tasks(due_at);
CREATE INDEX IF NOT EXISTS idx_tasks_open_by_due ON tasks(due_at) WHERE status IN ('Open', 'In Progress');

-- Priority sorting
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority, due_at) WHERE status IN ('Open', 'In Progress');

-- Task type
CREATE INDEX IF NOT EXISTS idx_tasks_task_type ON tasks(task_type);

-- Customer's tasks
CREATE INDEX IF NOT EXISTS idx_tasks_customer_status ON tasks(customer_id, status);

-- ============================================================================
-- NOTES TABLE INDEXES
-- ============================================================================

-- Customer ID with note type
CREATE INDEX IF NOT EXISTS idx_notes_customer_type ON notes(customer_id, note_type);

-- Note type filtering
CREATE INDEX IF NOT EXISTS idx_notes_note_type ON notes(note_type);

-- Promise to pay tracking
CREATE INDEX IF NOT EXISTS idx_notes_promise_pending ON notes(promise_date, promise_status)
    WHERE note_type = 'promise_to_pay' AND promise_status = 'pending';

-- Created at (for chronological display)
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC);

-- User's notes
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);

-- ============================================================================
-- DISPUTES TABLE INDEXES
-- ============================================================================

-- Status for open dispute tracking
CREATE INDEX IF NOT EXISTS idx_disputes_status_priority ON disputes(status, priority) WHERE status NOT IN ('Resolved', 'Rejected');

-- Assigned user
CREATE INDEX IF NOT EXISTS idx_disputes_assigned ON disputes(assigned_to_user_id) WHERE status NOT IN ('Resolved', 'Rejected');

-- Due date for SLA tracking
CREATE INDEX IF NOT EXISTS idx_disputes_due_date ON disputes(due_date) WHERE status NOT IN ('Resolved', 'Rejected');

-- Customer disputes
CREATE INDEX IF NOT EXISTS idx_disputes_customer_status ON disputes(customer_id, status);

-- ============================================================================
-- EMAIL_LOG TABLE INDEXES
-- ============================================================================

-- Customer emails by date
CREATE INDEX IF NOT EXISTS idx_email_log_customer_date ON email_log(customer_id, sent_at DESC);

-- Delivery status tracking
CREATE INDEX IF NOT EXISTS idx_email_log_delivery_status ON email_log(delivery_status) WHERE delivery_status IN ('pending', 'bounced', 'failed');

-- ============================================================================
-- CREDIT_HOLDS TABLE INDEXES
-- ============================================================================

-- Active holds
CREATE INDEX IF NOT EXISTS idx_credit_holds_active ON credit_holds(customer_id) WHERE is_active = TRUE;

-- Hold history
CREATE INDEX IF NOT EXISTS idx_credit_holds_placed ON credit_holds(placed_at DESC);

-- ============================================================================
-- ENABLE EXTENSIONS FOR ADVANCED FEATURES
-- ============================================================================

-- Enable pg_trgm extension for fuzzy text search (if not already enabled)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable btree_gin for better GIN index performance
CREATE EXTENSION IF NOT EXISTS btree_gin;

COMMIT;
