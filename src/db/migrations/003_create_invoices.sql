-- Migration: 003_create_invoices
-- Description: Create invoices table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- INVOICES TABLE
-- Purpose: Stores invoice/credit memo data synced from Epicor ERP
-- ============================================================================

BEGIN;

-- Create enum type for invoice status
DO $$ BEGIN
    CREATE TYPE invoice_status AS ENUM (
        'Open',
        'Paid',
        'Partial',
        'Disputed',
        'Written Off'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create enum type for invoice type
DO $$ BEGIN
    CREATE TYPE invoice_type AS ENUM (
        'Invoice',
        'Credit Memo',
        'Finance Charge',
        'Debit Memo'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create invoices table
CREATE TABLE IF NOT EXISTS invoices (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Epicor integration
    epicor_invoice_number VARCHAR(50) UNIQUE NOT NULL,

    -- Customer reference
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,

    -- Date information
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,

    -- Amount fields
    original_amount DECIMAL(15,2) NOT NULL,
    open_balance DECIMAL(15,2) NOT NULL,

    -- Status and type
    status VARCHAR(20) DEFAULT 'Open' NOT NULL CHECK (status IN ('Open', 'Paid', 'Partial', 'Disputed', 'Written Off')),
    invoice_type VARCHAR(20) DEFAULT 'Invoice' NOT NULL CHECK (invoice_type IN ('Invoice', 'Credit Memo', 'Finance Charge', 'Debit Memo')),

    -- Organization assignment
    branch_id VARCHAR(50),
    department VARCHAR(100),
    salesperson_id VARCHAR(50),

    -- Reference fields
    job_reference VARCHAR(100),
    po_reference VARCHAR(100),
    project_reference VARCHAR(100),
    order_number VARCHAR(50),
    ticket_number VARCHAR(50),

    -- Calculated fields (generated columns)
    days_past_due INTEGER GENERATED ALWAYS AS (
        GREATEST(0, CURRENT_DATE - due_date)
    ) STORED,

    aging_bucket VARCHAR(20) GENERATED ALWAYS AS (
        CASE
            WHEN CURRENT_DATE <= due_date THEN 'Current'
            WHEN CURRENT_DATE - due_date <= 30 THEN '1-30'
            WHEN CURRENT_DATE - due_date <= 60 THEN '31-60'
            WHEN CURRENT_DATE - due_date <= 90 THEN '61-90'
            ELSE '90+'
        END
    ) STORED,

    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_synced_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT invoices_due_date_check CHECK (due_date >= invoice_date),
    CONSTRAINT invoices_open_balance_check CHECK (
        (invoice_type = 'Credit Memo' AND open_balance <= 0) OR
        (invoice_type != 'Credit Memo' AND open_balance >= 0)
    ),
    CONSTRAINT invoices_amounts_match CHECK (
        (invoice_type = 'Credit Memo' AND original_amount <= 0) OR
        (invoice_type != 'Credit Memo' AND original_amount >= 0)
    )
);

-- Add table comment
COMMENT ON TABLE invoices IS 'Invoice and credit memo data synced from Epicor ERP - includes aging and payment status';

-- Add column comments
COMMENT ON COLUMN invoices.id IS 'Unique identifier for the invoice in AR Control Hub';
COMMENT ON COLUMN invoices.epicor_invoice_number IS 'Invoice number from Epicor ERP';
COMMENT ON COLUMN invoices.customer_id IS 'Reference to the customer';
COMMENT ON COLUMN invoices.invoice_date IS 'Date the invoice was created';
COMMENT ON COLUMN invoices.due_date IS 'Payment due date';
COMMENT ON COLUMN invoices.original_amount IS 'Original invoice amount';
COMMENT ON COLUMN invoices.open_balance IS 'Remaining unpaid balance';
COMMENT ON COLUMN invoices.status IS 'Invoice status: Open, Paid, Partial, Disputed, Written Off';
COMMENT ON COLUMN invoices.invoice_type IS 'Type: Invoice, Credit Memo, Finance Charge, Debit Memo';
COMMENT ON COLUMN invoices.branch_id IS 'Branch/location that owns this invoice';
COMMENT ON COLUMN invoices.department IS 'Department assignment';
COMMENT ON COLUMN invoices.salesperson_id IS 'Salesperson assigned to this invoice';
COMMENT ON COLUMN invoices.job_reference IS 'Related job number';
COMMENT ON COLUMN invoices.po_reference IS 'Customer PO number';
COMMENT ON COLUMN invoices.project_reference IS 'Related project number';
COMMENT ON COLUMN invoices.order_number IS 'Sales order number';
COMMENT ON COLUMN invoices.ticket_number IS 'Support ticket reference';
COMMENT ON COLUMN invoices.days_past_due IS 'Calculated days past due date (generated)';
COMMENT ON COLUMN invoices.aging_bucket IS 'Calculated aging bucket: Current, 1-30, 31-60, 61-90, 90+ (generated)';
COMMENT ON COLUMN invoices.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN invoices.updated_at IS 'Record last update timestamp';
COMMENT ON COLUMN invoices.last_synced_at IS 'Last sync from Epicor timestamp';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS invoices_updated_at ON invoices;
CREATE TRIGGER invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create basic index for foreign key
CREATE INDEX IF NOT EXISTS idx_invoices_customer_id ON invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_epicor_number ON invoices(epicor_invoice_number);

COMMIT;
