-- Migration: 004_create_payments
-- Description: Create payments table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- PAYMENTS TABLE
-- Purpose: Stores payment data synced from Epicor ERP
-- ============================================================================

BEGIN;

-- Create enum type for payment type
DO $$ BEGIN
    CREATE TYPE payment_type AS ENUM (
        'Check',
        'ACH',
        'Card',
        'Cash',
        'Wire',
        'Other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Epicor integration
    epicor_payment_id VARCHAR(50) UNIQUE NOT NULL,

    -- Customer reference
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,

    -- Payment details
    payment_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    payment_type VARCHAR(20) CHECK (payment_type IN ('Check', 'ACH', 'Card', 'Cash', 'Wire', 'Other')),

    -- Reference numbers
    check_number VARCHAR(50),
    reference_number VARCHAR(100),

    -- Unapplied tracking
    unapplied_amount DECIMAL(15,2) DEFAULT 0 NOT NULL,

    -- Additional info
    notes TEXT,

    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_synced_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT payments_amount_positive CHECK (amount > 0),
    CONSTRAINT payments_unapplied_valid CHECK (unapplied_amount >= 0 AND unapplied_amount <= amount)
);

-- Add table comment
COMMENT ON TABLE payments IS 'Payment records synced from Epicor ERP - includes check, ACH, card, and wire payments';

-- Add column comments
COMMENT ON COLUMN payments.id IS 'Unique identifier for the payment in AR Control Hub';
COMMENT ON COLUMN payments.epicor_payment_id IS 'Payment ID from Epicor ERP';
COMMENT ON COLUMN payments.customer_id IS 'Reference to the customer who made the payment';
COMMENT ON COLUMN payments.payment_date IS 'Date the payment was received';
COMMENT ON COLUMN payments.amount IS 'Total payment amount';
COMMENT ON COLUMN payments.payment_type IS 'Payment method: Check, ACH, Card, Cash, Wire, Other';
COMMENT ON COLUMN payments.check_number IS 'Check number if payment by check';
COMMENT ON COLUMN payments.reference_number IS 'Bank reference or transaction number';
COMMENT ON COLUMN payments.unapplied_amount IS 'Amount not yet applied to invoices';
COMMENT ON COLUMN payments.notes IS 'Additional notes about the payment';
COMMENT ON COLUMN payments.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN payments.last_synced_at IS 'Last sync from Epicor timestamp';

-- Create basic index for foreign key
CREATE INDEX IF NOT EXISTS idx_payments_customer_id ON payments(customer_id);
CREATE INDEX IF NOT EXISTS idx_payments_epicor_id ON payments(epicor_payment_id);

COMMIT;
