-- Migration: 008_create_alerts
-- Description: Create alerts table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- ALERTS TABLE
-- Purpose: Stores system-generated alerts for AR management
-- ============================================================================

BEGIN;

-- Create enum type for alert type
DO $$ BEGIN
    CREATE TYPE alert_type AS ENUM (
        'inactive_but_owing',
        'near_credit_limit',
        'over_credit_limit',
        'broken_promise',
        'long_overdue_60',
        'long_overdue_90',
        'unapplied_credits',
        'large_balance',
        'payment_returned',
        'new_dispute',
        'credit_hold_released',
        'high_risk_customer'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create enum type for alert severity
DO $$ BEGIN
    CREATE TYPE alert_severity AS ENUM (
        'Low',
        'Medium',
        'High',
        'Critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- References
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE SET NULL,

    -- Alert details
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN (
        'inactive_but_owing',
        'near_credit_limit',
        'over_credit_limit',
        'broken_promise',
        'long_overdue_60',
        'long_overdue_90',
        'unapplied_credits',
        'large_balance',
        'payment_returned',
        'new_dispute',
        'credit_hold_released',
        'high_risk_customer'
    )),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),

    -- Alert message
    title VARCHAR(255),
    message TEXT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Timing
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,

    -- Resolution
    resolved_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    resolution_note TEXT,

    -- Alert metadata (JSON for flexibility)
    metadata JSONB,

    -- Constraints
    CONSTRAINT alerts_resolved_status CHECK (
        (is_active = FALSE AND resolved_at IS NOT NULL) OR
        (is_active = TRUE AND resolved_at IS NULL)
    )
);

-- Add table comment
COMMENT ON TABLE alerts IS 'System-generated alerts for accounts requiring attention - credit limits, overdue invoices, broken promises';

-- Add column comments
COMMENT ON COLUMN alerts.id IS 'Unique identifier for the alert';
COMMENT ON COLUMN alerts.customer_id IS 'Reference to the customer this alert is about';
COMMENT ON COLUMN alerts.invoice_id IS 'Optional reference to a specific invoice';
COMMENT ON COLUMN alerts.alert_type IS 'Type of alert: inactive_but_owing, near_credit_limit, over_credit_limit, broken_promise, long_overdue_60, long_overdue_90, unapplied_credits, etc.';
COMMENT ON COLUMN alerts.severity IS 'Alert severity: Low, Medium, High, Critical';
COMMENT ON COLUMN alerts.title IS 'Short alert title for display';
COMMENT ON COLUMN alerts.message IS 'Detailed alert message';
COMMENT ON COLUMN alerts.is_active IS 'Whether the alert is still active/unresolved';
COMMENT ON COLUMN alerts.triggered_at IS 'When the alert was generated';
COMMENT ON COLUMN alerts.resolved_at IS 'When the alert was resolved';
COMMENT ON COLUMN alerts.resolved_by_user_id IS 'User who resolved the alert';
COMMENT ON COLUMN alerts.resolution_note IS 'Notes about how/why the alert was resolved';
COMMENT ON COLUMN alerts.metadata IS 'Additional alert data in JSON format';

-- Create indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_alerts_customer_id ON alerts(customer_id);
CREATE INDEX IF NOT EXISTS idx_alerts_invoice_id ON alerts(invoice_id);

COMMIT;
