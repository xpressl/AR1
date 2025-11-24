-- Migration: 006_create_notes
-- Description: Create notes table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- NOTES TABLE
-- Purpose: Stores collection notes, call logs, and promise-to-pay records
-- ============================================================================

BEGIN;

-- Create enum type for note type
DO $$ BEGIN
    CREATE TYPE note_type AS ENUM (
        'call',
        'email',
        'dispute',
        'internal',
        'promise_to_pay',
        'payment_reminder',
        'customer_contact'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create enum type for promise status
DO $$ BEGIN
    CREATE TYPE promise_status AS ENUM (
        'pending',
        'kept',
        'broken',
        'partial'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- References
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE SET NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,

    -- Note details
    note_type VARCHAR(30) NOT NULL CHECK (note_type IN ('call', 'email', 'dispute', 'internal', 'promise_to_pay', 'payment_reminder', 'customer_contact')),
    content TEXT NOT NULL,

    -- Promise-to-pay fields
    promise_amount DECIMAL(15,2) NULL,
    promise_date DATE NULL,
    promise_status VARCHAR(20) NULL CHECK (promise_status IS NULL OR promise_status IN ('pending', 'kept', 'broken', 'partial')),

    -- Contact info for this interaction
    contact_name VARCHAR(255),
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),

    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Constraints
    CONSTRAINT notes_promise_fields CHECK (
        (note_type = 'promise_to_pay' AND promise_amount IS NOT NULL AND promise_date IS NOT NULL AND promise_status IS NOT NULL) OR
        (note_type != 'promise_to_pay')
    ),
    CONSTRAINT notes_promise_amount_positive CHECK (promise_amount IS NULL OR promise_amount > 0),
    CONSTRAINT notes_content_not_empty CHECK (LENGTH(TRIM(content)) > 0)
);

-- Add table comment
COMMENT ON TABLE notes IS 'Collection notes, call logs, emails, and promise-to-pay records for customers and invoices';

-- Add column comments
COMMENT ON COLUMN notes.id IS 'Unique identifier for the note';
COMMENT ON COLUMN notes.customer_id IS 'Reference to the customer this note is about';
COMMENT ON COLUMN notes.invoice_id IS 'Optional reference to a specific invoice';
COMMENT ON COLUMN notes.user_id IS 'Reference to the user who created the note';
COMMENT ON COLUMN notes.note_type IS 'Type: call, email, dispute, internal, promise_to_pay, payment_reminder, customer_contact';
COMMENT ON COLUMN notes.content IS 'Note content/description';
COMMENT ON COLUMN notes.promise_amount IS 'For promise_to_pay: amount customer promised to pay';
COMMENT ON COLUMN notes.promise_date IS 'For promise_to_pay: date customer promised to pay by';
COMMENT ON COLUMN notes.promise_status IS 'For promise_to_pay: pending, kept, broken, partial';
COMMENT ON COLUMN notes.contact_name IS 'Name of person contacted';
COMMENT ON COLUMN notes.contact_phone IS 'Phone number used for contact';
COMMENT ON COLUMN notes.contact_email IS 'Email used for contact';
COMMENT ON COLUMN notes.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN notes.updated_at IS 'Record last update timestamp';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS notes_updated_at ON notes;
CREATE TRIGGER notes_updated_at
    BEFORE UPDATE ON notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_notes_customer_id ON notes(customer_id);
CREATE INDEX IF NOT EXISTS idx_notes_invoice_id ON notes(invoice_id);
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);

COMMIT;
