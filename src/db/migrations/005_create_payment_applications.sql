-- Migration: 005_create_payment_applications
-- Description: Create payment_applications table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- PAYMENT_APPLICATIONS TABLE
-- Purpose: Tracks how payments are applied to specific invoices
-- ============================================================================

BEGIN;

-- Create payment_applications table
CREATE TABLE IF NOT EXISTS payment_applications (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- References
    payment_id INTEGER NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,

    -- Application details
    amount_applied DECIMAL(15,2) NOT NULL,

    -- Audit timestamp
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Constraints
    CONSTRAINT payment_applications_amount_positive CHECK (amount_applied > 0),
    CONSTRAINT payment_applications_unique UNIQUE (payment_id, invoice_id)
);

-- Add table comment
COMMENT ON TABLE payment_applications IS 'Junction table tracking how payments are applied to invoices';

-- Add column comments
COMMENT ON COLUMN payment_applications.id IS 'Unique identifier for the payment application';
COMMENT ON COLUMN payment_applications.payment_id IS 'Reference to the payment being applied';
COMMENT ON COLUMN payment_applications.invoice_id IS 'Reference to the invoice receiving the payment';
COMMENT ON COLUMN payment_applications.amount_applied IS 'Amount from the payment applied to this invoice';
COMMENT ON COLUMN payment_applications.applied_at IS 'Timestamp when the application was recorded';

-- Create indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_payment_applications_payment_id ON payment_applications(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_applications_invoice_id ON payment_applications(invoice_id);

-- Create function to validate payment application doesn't exceed payment amount
CREATE OR REPLACE FUNCTION validate_payment_application()
RETURNS TRIGGER AS $$
DECLARE
    total_applied DECIMAL(15,2);
    payment_amount DECIMAL(15,2);
BEGIN
    -- Get the payment amount
    SELECT amount INTO payment_amount FROM payments WHERE id = NEW.payment_id;

    -- Calculate total applied including this new application
    SELECT COALESCE(SUM(amount_applied), 0) INTO total_applied
    FROM payment_applications
    WHERE payment_id = NEW.payment_id AND id != COALESCE(NEW.id, 0);

    total_applied := total_applied + NEW.amount_applied;

    -- Check if total applied exceeds payment amount
    IF total_applied > payment_amount THEN
        RAISE EXCEPTION 'Total applied amount (%) exceeds payment amount (%)', total_applied, payment_amount;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to validate payment applications
DROP TRIGGER IF EXISTS validate_payment_application_trigger ON payment_applications;
CREATE TRIGGER validate_payment_application_trigger
    BEFORE INSERT OR UPDATE ON payment_applications
    FOR EACH ROW
    EXECUTE FUNCTION validate_payment_application();

-- Create function to update payment unapplied_amount
CREATE OR REPLACE FUNCTION update_payment_unapplied()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the unapplied amount on the payment
    IF TG_OP = 'DELETE' THEN
        UPDATE payments
        SET unapplied_amount = amount - COALESCE((
            SELECT SUM(amount_applied) FROM payment_applications WHERE payment_id = OLD.payment_id
        ), 0)
        WHERE id = OLD.payment_id;
        RETURN OLD;
    ELSE
        UPDATE payments
        SET unapplied_amount = amount - COALESCE((
            SELECT SUM(amount_applied) FROM payment_applications WHERE payment_id = NEW.payment_id
        ), 0)
        WHERE id = NEW.payment_id;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update payment unapplied_amount
DROP TRIGGER IF EXISTS update_payment_unapplied_trigger ON payment_applications;
CREATE TRIGGER update_payment_unapplied_trigger
    AFTER INSERT OR UPDATE OR DELETE ON payment_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_payment_unapplied();

-- Create function to update invoice open_balance and status
CREATE OR REPLACE FUNCTION update_invoice_balance()
RETURNS TRIGGER AS $$
DECLARE
    total_applied DECIMAL(15,2);
    orig_amount DECIMAL(15,2);
    new_balance DECIMAL(15,2);
    new_status VARCHAR(20);
BEGIN
    -- Determine which invoice to update
    IF TG_OP = 'DELETE' THEN
        -- Get original amount
        SELECT original_amount INTO orig_amount FROM invoices WHERE id = OLD.invoice_id;

        -- Calculate total applied to this invoice
        SELECT COALESCE(SUM(amount_applied), 0) INTO total_applied
        FROM payment_applications WHERE invoice_id = OLD.invoice_id;

        new_balance := ABS(orig_amount) - total_applied;

        -- Determine new status
        IF new_balance <= 0 THEN
            new_status := 'Paid';
        ELSIF new_balance < ABS(orig_amount) THEN
            new_status := 'Partial';
        ELSE
            new_status := 'Open';
        END IF;

        -- Update the invoice (only if not disputed or written off)
        UPDATE invoices
        SET open_balance = CASE WHEN original_amount < 0 THEN -new_balance ELSE new_balance END,
            status = CASE WHEN status IN ('Disputed', 'Written Off') THEN status ELSE new_status END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = OLD.invoice_id;

        RETURN OLD;
    ELSE
        -- Get original amount
        SELECT original_amount INTO orig_amount FROM invoices WHERE id = NEW.invoice_id;

        -- Calculate total applied to this invoice
        SELECT COALESCE(SUM(amount_applied), 0) INTO total_applied
        FROM payment_applications WHERE invoice_id = NEW.invoice_id;

        new_balance := ABS(orig_amount) - total_applied;

        -- Determine new status
        IF new_balance <= 0 THEN
            new_status := 'Paid';
        ELSIF new_balance < ABS(orig_amount) THEN
            new_status := 'Partial';
        ELSE
            new_status := 'Open';
        END IF;

        -- Update the invoice (only if not disputed or written off)
        UPDATE invoices
        SET open_balance = CASE WHEN original_amount < 0 THEN -new_balance ELSE new_balance END,
            status = CASE WHEN status IN ('Disputed', 'Written Off') THEN status ELSE new_status END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.invoice_id;

        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update invoice balance
DROP TRIGGER IF EXISTS update_invoice_balance_trigger ON payment_applications;
CREATE TRIGGER update_invoice_balance_trigger
    AFTER INSERT OR UPDATE OR DELETE ON payment_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_invoice_balance();

COMMIT;
