-- Migration: 009_create_disputes
-- Description: Create disputes table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- DISPUTES TABLE
-- Purpose: Tracks invoice disputes and their resolution
-- ============================================================================

BEGIN;

-- Create enum type for dispute reason code
DO $$ BEGIN
    CREATE TYPE dispute_reason_code AS ENUM (
        'pricing',
        'damaged',
        'short_ship',
        'wrong_item',
        'tax',
        'duplicate',
        'not_received',
        'quality',
        'late_delivery',
        'unauthorized',
        'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create enum type for dispute status
DO $$ BEGIN
    CREATE TYPE dispute_status AS ENUM (
        'Open',
        'In Review',
        'Pending Customer',
        'Pending Internal',
        'Resolved',
        'Rejected',
        'Escalated'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create disputes table
CREATE TABLE IF NOT EXISTS disputes (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- References
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    assigned_to_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Dispute details
    reason_code VARCHAR(50) NOT NULL CHECK (reason_code IN (
        'pricing',
        'damaged',
        'short_ship',
        'wrong_item',
        'tax',
        'duplicate',
        'not_received',
        'quality',
        'late_delivery',
        'unauthorized',
        'other'
    )),
    description TEXT,
    disputed_amount DECIMAL(15,2) NOT NULL,

    -- Supporting documentation
    customer_reference VARCHAR(100),
    internal_reference VARCHAR(100),

    -- Status
    status VARCHAR(20) DEFAULT 'Open' NOT NULL CHECK (status IN (
        'Open',
        'In Review',
        'Pending Customer',
        'Pending Internal',
        'Resolved',
        'Rejected',
        'Escalated'
    )),
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),

    -- Resolution
    resolution_type VARCHAR(50), -- credit_issued, write_off, rejected, partial_credit
    resolution_amount DECIMAL(15,2),
    resolution_note TEXT,
    credit_memo_number VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    due_date DATE, -- SLA tracking

    -- Constraints
    CONSTRAINT disputes_disputed_amount_positive CHECK (disputed_amount > 0),
    CONSTRAINT disputes_resolved_status CHECK (
        (status IN ('Resolved', 'Rejected') AND resolved_at IS NOT NULL) OR
        (status NOT IN ('Resolved', 'Rejected'))
    ),
    CONSTRAINT disputes_resolution_amount CHECK (
        resolution_amount IS NULL OR resolution_amount >= 0
    )
);

-- Add table comment
COMMENT ON TABLE disputes IS 'Invoice disputes tracking - includes reason codes, status, and resolution details';

-- Add column comments
COMMENT ON COLUMN disputes.id IS 'Unique identifier for the dispute';
COMMENT ON COLUMN disputes.customer_id IS 'Reference to the customer';
COMMENT ON COLUMN disputes.invoice_id IS 'Reference to the disputed invoice';
COMMENT ON COLUMN disputes.assigned_to_user_id IS 'User assigned to resolve this dispute';
COMMENT ON COLUMN disputes.created_by_user_id IS 'User who created this dispute record';
COMMENT ON COLUMN disputes.reason_code IS 'Dispute reason: pricing, damaged, short_ship, wrong_item, tax, duplicate, not_received, quality, late_delivery, unauthorized, other';
COMMENT ON COLUMN disputes.description IS 'Detailed description of the dispute';
COMMENT ON COLUMN disputes.disputed_amount IS 'Amount being disputed';
COMMENT ON COLUMN disputes.customer_reference IS 'Customer reference number for this dispute';
COMMENT ON COLUMN disputes.internal_reference IS 'Internal reference number';
COMMENT ON COLUMN disputes.status IS 'Status: Open, In Review, Pending Customer, Pending Internal, Resolved, Rejected, Escalated';
COMMENT ON COLUMN disputes.priority IS 'Priority level 1-10 (1=highest)';
COMMENT ON COLUMN disputes.resolution_type IS 'How the dispute was resolved';
COMMENT ON COLUMN disputes.resolution_amount IS 'Amount credited or adjusted';
COMMENT ON COLUMN disputes.resolution_note IS 'Notes about the resolution';
COMMENT ON COLUMN disputes.credit_memo_number IS 'Credit memo number if one was issued';
COMMENT ON COLUMN disputes.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN disputes.updated_at IS 'Record last update timestamp';
COMMENT ON COLUMN disputes.resolved_at IS 'When the dispute was resolved';
COMMENT ON COLUMN disputes.due_date IS 'SLA due date for resolution';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS disputes_updated_at ON disputes;
CREATE TRIGGER disputes_updated_at
    BEFORE UPDATE ON disputes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to update invoice status when dispute is created/resolved
CREATE OR REPLACE FUNCTION update_invoice_dispute_status()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Mark invoice as disputed
        UPDATE invoices
        SET status = 'Disputed',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.invoice_id AND status NOT IN ('Written Off');
    ELSIF TG_OP = 'UPDATE' AND NEW.status IN ('Resolved', 'Rejected') AND OLD.status NOT IN ('Resolved', 'Rejected') THEN
        -- Check if there are other active disputes for this invoice
        IF NOT EXISTS (
            SELECT 1 FROM disputes
            WHERE invoice_id = NEW.invoice_id
            AND id != NEW.id
            AND status NOT IN ('Resolved', 'Rejected')
        ) THEN
            -- No other active disputes, update invoice status based on balance
            UPDATE invoices
            SET status = CASE
                WHEN open_balance <= 0 THEN 'Paid'
                WHEN open_balance < original_amount THEN 'Partial'
                ELSE 'Open'
            END,
            updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.invoice_id AND status = 'Disputed';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update invoice status
DROP TRIGGER IF EXISTS update_invoice_dispute_status_trigger ON disputes;
CREATE TRIGGER update_invoice_dispute_status_trigger
    AFTER INSERT OR UPDATE ON disputes
    FOR EACH ROW
    EXECUTE FUNCTION update_invoice_dispute_status();

-- Create indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_disputes_customer_id ON disputes(customer_id);
CREATE INDEX IF NOT EXISTS idx_disputes_invoice_id ON disputes(invoice_id);
CREATE INDEX IF NOT EXISTS idx_disputes_assigned_to ON disputes(assigned_to_user_id);
CREATE INDEX IF NOT EXISTS idx_disputes_status ON disputes(status);

COMMIT;
