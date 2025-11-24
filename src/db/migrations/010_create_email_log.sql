-- Migration: 010_create_email_log
-- Description: Create email_log table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- EMAIL_LOG TABLE
-- Purpose: Tracks all emails sent to customers for AR purposes
-- ============================================================================

BEGIN;

-- Create enum type for email type
DO $$ BEGIN
    CREATE TYPE email_type AS ENUM (
        'statement',
        'reminder',
        'notice',
        'past_due_notice',
        'final_notice',
        'custom',
        'dispute_notification',
        'payment_confirmation',
        'credit_hold_notice'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create enum type for delivery status
DO $$ BEGIN
    CREATE TYPE email_delivery_status AS ENUM (
        'pending',
        'sent',
        'delivered',
        'bounced',
        'failed',
        'opened',
        'clicked'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create email_log table
CREATE TABLE IF NOT EXISTS email_log (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- References
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE SET NULL,
    sent_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Email details
    email_type VARCHAR(30) NOT NULL CHECK (email_type IN (
        'statement',
        'reminder',
        'notice',
        'past_due_notice',
        'final_notice',
        'custom',
        'dispute_notification',
        'payment_confirmation',
        'credit_hold_notice'
    )),
    template_used VARCHAR(50),

    -- Recipient info
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(255),
    cc_emails TEXT[], -- Array of CC email addresses

    -- Email content
    subject VARCHAR(255) NOT NULL,
    body TEXT,
    body_html TEXT,

    -- Attachments
    has_attachments BOOLEAN DEFAULT FALSE,
    attachment_names TEXT[], -- Array of attachment filenames

    -- Timing
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Delivery tracking
    delivery_status VARCHAR(20) DEFAULT 'sent' NOT NULL CHECK (delivery_status IN (
        'pending',
        'sent',
        'delivered',
        'bounced',
        'failed',
        'opened',
        'clicked'
    )),
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    bounce_reason TEXT,

    -- External tracking
    external_message_id VARCHAR(255),
    tracking_id VARCHAR(100),

    -- Constraints
    CONSTRAINT email_log_recipient_format CHECK (recipient_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Add table comment
COMMENT ON TABLE email_log IS 'Log of all emails sent for AR purposes - statements, reminders, notices';

-- Add column comments
COMMENT ON COLUMN email_log.id IS 'Unique identifier for the email';
COMMENT ON COLUMN email_log.customer_id IS 'Reference to the customer';
COMMENT ON COLUMN email_log.invoice_id IS 'Optional reference to a specific invoice';
COMMENT ON COLUMN email_log.sent_by_user_id IS 'User who sent or triggered the email';
COMMENT ON COLUMN email_log.email_type IS 'Type: statement, reminder, notice, past_due_notice, final_notice, custom, dispute_notification, payment_confirmation, credit_hold_notice';
COMMENT ON COLUMN email_log.template_used IS 'Template name/ID used for this email';
COMMENT ON COLUMN email_log.recipient_email IS 'Email address of primary recipient';
COMMENT ON COLUMN email_log.recipient_name IS 'Name of primary recipient';
COMMENT ON COLUMN email_log.cc_emails IS 'Array of CC email addresses';
COMMENT ON COLUMN email_log.subject IS 'Email subject line';
COMMENT ON COLUMN email_log.body IS 'Plain text email body';
COMMENT ON COLUMN email_log.body_html IS 'HTML email body';
COMMENT ON COLUMN email_log.has_attachments IS 'Whether the email had attachments';
COMMENT ON COLUMN email_log.attachment_names IS 'Array of attachment filenames';
COMMENT ON COLUMN email_log.scheduled_at IS 'When the email was scheduled (if queued)';
COMMENT ON COLUMN email_log.sent_at IS 'When the email was sent';
COMMENT ON COLUMN email_log.delivery_status IS 'Delivery status: pending, sent, delivered, bounced, failed, opened, clicked';
COMMENT ON COLUMN email_log.opened_at IS 'When the email was opened';
COMMENT ON COLUMN email_log.clicked_at IS 'When a link in the email was clicked';
COMMENT ON COLUMN email_log.bounce_reason IS 'Reason for bounce if bounced';
COMMENT ON COLUMN email_log.external_message_id IS 'Message ID from email provider';
COMMENT ON COLUMN email_log.tracking_id IS 'Tracking ID for open/click tracking';

-- Create indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_email_log_customer_id ON email_log(customer_id);
CREATE INDEX IF NOT EXISTS idx_email_log_invoice_id ON email_log(invoice_id);
CREATE INDEX IF NOT EXISTS idx_email_log_sent_at ON email_log(sent_at);
CREATE INDEX IF NOT EXISTS idx_email_log_email_type ON email_log(email_type);

COMMIT;
