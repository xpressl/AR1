-- Migration: 011_create_import_runs
-- Description: Create import_runs table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- IMPORT_RUNS TABLE
-- Purpose: Tracks Epicor data import/sync operations
-- ============================================================================

BEGIN;

-- Create enum type for import status
DO $$ BEGIN
    CREATE TYPE import_status AS ENUM (
        'Running',
        'Success',
        'Failed',
        'Partial',
        'Cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create enum type for import type
DO $$ BEGIN
    CREATE TYPE import_type AS ENUM (
        'full',
        'incremental',
        'customers_only',
        'invoices_only',
        'payments_only',
        'manual'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create import_runs table
CREATE TABLE IF NOT EXISTS import_runs (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Import details
    import_type VARCHAR(30) DEFAULT 'incremental' CHECK (import_type IN (
        'full',
        'incremental',
        'customers_only',
        'invoices_only',
        'payments_only',
        'manual'
    )),

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP WITH TIME ZONE,

    -- Status
    status VARCHAR(20) DEFAULT 'Running' NOT NULL CHECK (status IN (
        'Running',
        'Success',
        'Failed',
        'Partial',
        'Cancelled'
    )),
    error_message TEXT,
    error_details JSONB,

    -- Statistics - Customers
    customers_processed INTEGER DEFAULT 0 NOT NULL,
    customers_imported INTEGER DEFAULT 0 NOT NULL,
    customers_updated INTEGER DEFAULT 0 NOT NULL,
    customers_errors INTEGER DEFAULT 0 NOT NULL,

    -- Statistics - Invoices
    invoices_processed INTEGER DEFAULT 0 NOT NULL,
    invoices_imported INTEGER DEFAULT 0 NOT NULL,
    invoices_updated INTEGER DEFAULT 0 NOT NULL,
    invoices_errors INTEGER DEFAULT 0 NOT NULL,

    -- Statistics - Payments
    payments_processed INTEGER DEFAULT 0 NOT NULL,
    payments_imported INTEGER DEFAULT 0 NOT NULL,
    payments_updated INTEGER DEFAULT 0 NOT NULL,
    payments_errors INTEGER DEFAULT 0 NOT NULL,

    -- Statistics - Alerts
    alerts_generated INTEGER DEFAULT 0 NOT NULL,
    alerts_resolved INTEGER DEFAULT 0 NOT NULL,

    -- Triggered by
    triggered_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    trigger_type VARCHAR(20) DEFAULT 'scheduled' CHECK (trigger_type IN ('scheduled', 'manual', 'webhook')),

    -- Performance metrics
    duration_seconds INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN finished_at IS NOT NULL THEN EXTRACT(EPOCH FROM (finished_at - started_at))::INTEGER
            ELSE NULL
        END
    ) STORED,

    -- Data range (for incremental imports)
    data_from_date TIMESTAMP WITH TIME ZONE,
    data_to_date TIMESTAMP WITH TIME ZONE
);

-- Add table comment
COMMENT ON TABLE import_runs IS 'Log of all data import/sync runs from Epicor ERP';

-- Add column comments
COMMENT ON COLUMN import_runs.id IS 'Unique identifier for the import run';
COMMENT ON COLUMN import_runs.import_type IS 'Type of import: full, incremental, customers_only, invoices_only, payments_only, manual';
COMMENT ON COLUMN import_runs.started_at IS 'When the import started';
COMMENT ON COLUMN import_runs.finished_at IS 'When the import finished';
COMMENT ON COLUMN import_runs.status IS 'Status: Running, Success, Failed, Partial, Cancelled';
COMMENT ON COLUMN import_runs.error_message IS 'Error message if import failed';
COMMENT ON COLUMN import_runs.error_details IS 'Detailed error information in JSON format';
COMMENT ON COLUMN import_runs.customers_processed IS 'Total customers processed';
COMMENT ON COLUMN import_runs.customers_imported IS 'New customers created';
COMMENT ON COLUMN import_runs.customers_updated IS 'Existing customers updated';
COMMENT ON COLUMN import_runs.customers_errors IS 'Customer records with errors';
COMMENT ON COLUMN import_runs.invoices_processed IS 'Total invoices processed';
COMMENT ON COLUMN import_runs.invoices_imported IS 'New invoices created';
COMMENT ON COLUMN import_runs.invoices_updated IS 'Existing invoices updated';
COMMENT ON COLUMN import_runs.invoices_errors IS 'Invoice records with errors';
COMMENT ON COLUMN import_runs.payments_processed IS 'Total payments processed';
COMMENT ON COLUMN import_runs.payments_imported IS 'New payments created';
COMMENT ON COLUMN import_runs.payments_updated IS 'Existing payments updated';
COMMENT ON COLUMN import_runs.payments_errors IS 'Payment records with errors';
COMMENT ON COLUMN import_runs.alerts_generated IS 'New alerts generated during import';
COMMENT ON COLUMN import_runs.alerts_resolved IS 'Alerts auto-resolved during import';
COMMENT ON COLUMN import_runs.triggered_by_user_id IS 'User who triggered the import (if manual)';
COMMENT ON COLUMN import_runs.trigger_type IS 'How the import was triggered: scheduled, manual, webhook';
COMMENT ON COLUMN import_runs.duration_seconds IS 'Import duration in seconds (calculated)';
COMMENT ON COLUMN import_runs.data_from_date IS 'Start of data range for incremental import';
COMMENT ON COLUMN import_runs.data_to_date IS 'End of data range for incremental import';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_import_runs_started_at ON import_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_import_runs_status ON import_runs(status);

COMMIT;
