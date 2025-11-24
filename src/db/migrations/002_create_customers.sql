-- Migration: 002_create_customers
-- Description: Create customers table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- CUSTOMERS TABLE
-- Purpose: Stores customer master data synced from Epicor ERP
-- ============================================================================

BEGIN;

-- Create enum type for customer status
DO $$ BEGIN
    CREATE TYPE customer_status AS ENUM (
        'Active',
        'Inactive',
        'On Hold',
        'COD'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Epicor integration
    epicor_customer_id VARCHAR(50) UNIQUE NOT NULL,

    -- Basic information
    name VARCHAR(255) NOT NULL,
    dba_trade_name VARCHAR(255),

    -- Billing address
    billing_address_line1 VARCHAR(255),
    billing_address_line2 VARCHAR(255),
    billing_city VARCHAR(100),
    billing_state VARCHAR(50),
    billing_zip VARCHAR(20),

    -- Contact information
    billing_email VARCHAR(255),
    billing_phone VARCHAR(50),
    primary_contact_name VARCHAR(255),

    -- Sales assignment
    salesperson_id VARCHAR(50),
    salesperson_name VARCHAR(255),

    -- Terms and credit
    terms_code VARCHAR(20),
    credit_limit DECIMAL(15,2) DEFAULT 0,
    current_balance DECIMAL(15,2) DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'Active' NOT NULL CHECK (status IN ('Active', 'Inactive', 'On Hold', 'COD')),

    -- Classification
    customer_type VARCHAR(50),
    branch_id VARCHAR(50),
    department VARCHAR(100),

    -- Tax information
    tax_status VARCHAR(20),
    tax_exempt_number VARCHAR(50),

    -- Activity tracking
    last_invoice_date DATE,
    last_payment_date DATE,

    -- Calculated fields (generated columns)
    days_since_last_invoice INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN last_invoice_date IS NOT NULL THEN CURRENT_DATE - last_invoice_date
            ELSE NULL
        END
    ) STORED,

    credit_utilization DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE
            WHEN credit_limit > 0 THEN ROUND((current_balance / credit_limit * 100)::numeric, 2)
            ELSE 0
        END
    ) STORED,

    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_synced_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT customers_credit_limit_positive CHECK (credit_limit >= 0),
    CONSTRAINT customers_email_format CHECK (billing_email IS NULL OR billing_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Add table comment
COMMENT ON TABLE customers IS 'Customer master data synced from Epicor ERP - includes billing info, credit terms, and status';

-- Add column comments
COMMENT ON COLUMN customers.id IS 'Unique identifier for the customer in AR Control Hub';
COMMENT ON COLUMN customers.epicor_customer_id IS 'Customer ID from Epicor ERP (CustID)';
COMMENT ON COLUMN customers.name IS 'Customer company name';
COMMENT ON COLUMN customers.dba_trade_name IS 'Doing Business As / Trade Name';
COMMENT ON COLUMN customers.billing_address_line1 IS 'Primary billing address line';
COMMENT ON COLUMN customers.billing_address_line2 IS 'Secondary billing address line';
COMMENT ON COLUMN customers.billing_city IS 'Billing city';
COMMENT ON COLUMN customers.billing_state IS 'Billing state/province';
COMMENT ON COLUMN customers.billing_zip IS 'Billing postal code';
COMMENT ON COLUMN customers.billing_email IS 'Primary email for AR communications';
COMMENT ON COLUMN customers.billing_phone IS 'Primary phone for AR communications';
COMMENT ON COLUMN customers.primary_contact_name IS 'Name of primary AR contact';
COMMENT ON COLUMN customers.salesperson_id IS 'Assigned salesperson ID from Epicor';
COMMENT ON COLUMN customers.salesperson_name IS 'Assigned salesperson name';
COMMENT ON COLUMN customers.terms_code IS 'Payment terms code (NET30, NET60, etc.)';
COMMENT ON COLUMN customers.credit_limit IS 'Customer credit limit in dollars';
COMMENT ON COLUMN customers.current_balance IS 'Current outstanding AR balance';
COMMENT ON COLUMN customers.status IS 'Customer status: Active, Inactive, On Hold, COD';
COMMENT ON COLUMN customers.customer_type IS 'Customer classification/type';
COMMENT ON COLUMN customers.branch_id IS 'Assigned branch/location ID';
COMMENT ON COLUMN customers.department IS 'Department assignment';
COMMENT ON COLUMN customers.tax_status IS 'Tax status (Taxable, Exempt, etc.)';
COMMENT ON COLUMN customers.tax_exempt_number IS 'Tax exemption certificate number';
COMMENT ON COLUMN customers.last_invoice_date IS 'Date of most recent invoice';
COMMENT ON COLUMN customers.last_payment_date IS 'Date of most recent payment';
COMMENT ON COLUMN customers.days_since_last_invoice IS 'Calculated days since last invoice (generated)';
COMMENT ON COLUMN customers.credit_utilization IS 'Calculated credit utilization percentage (generated)';
COMMENT ON COLUMN customers.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN customers.updated_at IS 'Record last update timestamp';
COMMENT ON COLUMN customers.last_synced_at IS 'Last sync from Epicor timestamp';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS customers_updated_at ON customers;
CREATE TRIGGER customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create basic indexes (main indexes in 013_create_indexes.sql)
CREATE INDEX IF NOT EXISTS idx_customers_epicor_id ON customers(epicor_customer_id);
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);

COMMIT;
