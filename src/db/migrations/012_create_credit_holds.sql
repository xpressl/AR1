-- Migration: 012_create_credit_holds
-- Description: Create credit_holds table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- CREDIT_HOLDS TABLE
-- Purpose: Tracks customer credit holds and releases
-- ============================================================================

BEGIN;

-- Create enum type for credit hold reason
DO $$ BEGIN
    CREATE TYPE credit_hold_reason AS ENUM (
        'over_credit_limit',
        'past_due',
        'nsf_check',
        'bankruptcy',
        'collection',
        'management_decision',
        'new_customer',
        'credit_review',
        'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create credit_holds table
CREATE TABLE IF NOT EXISTS credit_holds (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Customer reference
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,

    -- Hold details
    placed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    placed_by_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    reason_code VARCHAR(50) CHECK (reason_code IN (
        'over_credit_limit',
        'past_due',
        'nsf_check',
        'bankruptcy',
        'collection',
        'management_decision',
        'new_customer',
        'credit_review',
        'other'
    )),
    reason_note TEXT,

    -- Amount information at time of hold
    balance_at_hold DECIMAL(15,2),
    credit_limit_at_hold DECIMAL(15,2),
    oldest_invoice_days INTEGER,

    -- Release details
    released_at TIMESTAMP WITH TIME ZONE,
    released_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    release_note TEXT,
    release_reason VARCHAR(50), -- payment_received, credit_increased, management_override, etc.

    -- Status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Epicor sync
    synced_to_epicor BOOLEAN DEFAULT FALSE,
    synced_at TIMESTAMP WITH TIME ZONE,
    epicor_hold_code VARCHAR(20),

    -- Constraints
    CONSTRAINT credit_holds_release_status CHECK (
        (is_active = TRUE AND released_at IS NULL AND released_by_user_id IS NULL) OR
        (is_active = FALSE AND released_at IS NOT NULL)
    )
);

-- Add table comment
COMMENT ON TABLE credit_holds IS 'Credit hold history - tracks when customers are placed on and released from credit hold';

-- Add column comments
COMMENT ON COLUMN credit_holds.id IS 'Unique identifier for the credit hold';
COMMENT ON COLUMN credit_holds.customer_id IS 'Reference to the customer on hold';
COMMENT ON COLUMN credit_holds.placed_at IS 'When the hold was placed';
COMMENT ON COLUMN credit_holds.placed_by_user_id IS 'User who placed the hold';
COMMENT ON COLUMN credit_holds.reason_code IS 'Reason: over_credit_limit, past_due, nsf_check, bankruptcy, collection, management_decision, new_customer, credit_review, other';
COMMENT ON COLUMN credit_holds.reason_note IS 'Additional notes about the hold';
COMMENT ON COLUMN credit_holds.balance_at_hold IS 'Customer balance when hold was placed';
COMMENT ON COLUMN credit_holds.credit_limit_at_hold IS 'Customer credit limit when hold was placed';
COMMENT ON COLUMN credit_holds.oldest_invoice_days IS 'Days past due of oldest invoice when hold was placed';
COMMENT ON COLUMN credit_holds.released_at IS 'When the hold was released';
COMMENT ON COLUMN credit_holds.released_by_user_id IS 'User who released the hold';
COMMENT ON COLUMN credit_holds.release_note IS 'Notes about the release';
COMMENT ON COLUMN credit_holds.release_reason IS 'Reason for release';
COMMENT ON COLUMN credit_holds.is_active IS 'Whether the hold is currently active';
COMMENT ON COLUMN credit_holds.synced_to_epicor IS 'Whether hold status was synced to Epicor';
COMMENT ON COLUMN credit_holds.synced_at IS 'When the hold was synced to Epicor';
COMMENT ON COLUMN credit_holds.epicor_hold_code IS 'Epicor hold code used';

-- Create function to update customer status when hold is placed/released
CREATE OR REPLACE FUNCTION update_customer_hold_status()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.is_active = TRUE THEN
        -- Place customer on hold
        UPDATE customers
        SET status = 'On Hold',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.customer_id AND status != 'Inactive';
    ELSIF TG_OP = 'UPDATE' AND OLD.is_active = TRUE AND NEW.is_active = FALSE THEN
        -- Check if there are other active holds
        IF NOT EXISTS (
            SELECT 1 FROM credit_holds
            WHERE customer_id = NEW.customer_id
            AND id != NEW.id
            AND is_active = TRUE
        ) THEN
            -- No other active holds, release customer
            UPDATE customers
            SET status = 'Active',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.customer_id AND status = 'On Hold';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update customer status
DROP TRIGGER IF EXISTS update_customer_hold_status_trigger ON credit_holds;
CREATE TRIGGER update_customer_hold_status_trigger
    AFTER INSERT OR UPDATE ON credit_holds
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_hold_status();

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_credit_holds_customer_id ON credit_holds(customer_id);
CREATE INDEX IF NOT EXISTS idx_credit_holds_is_active ON credit_holds(is_active);
CREATE INDEX IF NOT EXISTS idx_credit_holds_placed_at ON credit_holds(placed_at DESC);

COMMIT;
