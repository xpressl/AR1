-- Migration: 007_create_tasks
-- Description: Create tasks table for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- TASKS TABLE
-- Purpose: Stores collection tasks, follow-ups, and reminders
-- ============================================================================

BEGIN;

-- Create enum type for task type
DO $$ BEGIN
    CREATE TYPE task_type AS ENUM (
        'collection_call',
        'follow_up',
        'dispute_resolution',
        'review',
        'send_statement',
        'send_reminder',
        'credit_review',
        'escalation',
        'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create enum type for task status
DO $$ BEGIN
    CREATE TYPE task_status AS ENUM (
        'Open',
        'In Progress',
        'Completed',
        'Canceled',
        'Snoozed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- References
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE SET NULL,
    assigned_to_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Task details
    task_type VARCHAR(30) NOT NULL CHECK (task_type IN ('collection_call', 'follow_up', 'dispute_resolution', 'review', 'send_statement', 'send_reminder', 'credit_review', 'escalation', 'other')),
    description TEXT,

    -- Scheduling
    due_at TIMESTAMP WITH TIME ZONE NOT NULL,
    snoozed_until TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Status and priority
    status VARCHAR(20) DEFAULT 'Open' NOT NULL CHECK (status IN ('Open', 'In Progress', 'Completed', 'Canceled', 'Snoozed')),
    priority INTEGER DEFAULT 5 NOT NULL CHECK (priority >= 1 AND priority <= 10),

    -- Recurrence (for recurring tasks)
    is_recurring BOOLEAN DEFAULT FALSE NOT NULL,
    recurrence_pattern VARCHAR(50), -- daily, weekly, monthly, custom
    parent_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,

    -- Result tracking
    result_notes TEXT,

    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Constraints
    CONSTRAINT tasks_completed_status CHECK (
        (status = 'Completed' AND completed_at IS NOT NULL) OR
        (status != 'Completed')
    ),
    CONSTRAINT tasks_snoozed_status CHECK (
        (status = 'Snoozed' AND snoozed_until IS NOT NULL) OR
        (status != 'Snoozed')
    ),
    CONSTRAINT tasks_priority_range CHECK (priority >= 1 AND priority <= 10)
);

-- Add table comment
COMMENT ON TABLE tasks IS 'Collection tasks, follow-ups, and reminders assigned to AR team members';

-- Add column comments
COMMENT ON COLUMN tasks.id IS 'Unique identifier for the task';
COMMENT ON COLUMN tasks.customer_id IS 'Reference to the customer this task is for';
COMMENT ON COLUMN tasks.invoice_id IS 'Optional reference to a specific invoice';
COMMENT ON COLUMN tasks.assigned_to_user_id IS 'User responsible for completing this task';
COMMENT ON COLUMN tasks.created_by_user_id IS 'User who created this task';
COMMENT ON COLUMN tasks.task_type IS 'Type: collection_call, follow_up, dispute_resolution, review, send_statement, send_reminder, credit_review, escalation, other';
COMMENT ON COLUMN tasks.description IS 'Task description and notes';
COMMENT ON COLUMN tasks.due_at IS 'When the task should be completed';
COMMENT ON COLUMN tasks.snoozed_until IS 'If snoozed, when to resurface the task';
COMMENT ON COLUMN tasks.completed_at IS 'When the task was completed';
COMMENT ON COLUMN tasks.status IS 'Status: Open, In Progress, Completed, Canceled, Snoozed';
COMMENT ON COLUMN tasks.priority IS 'Priority level 1-10 (1=highest, 10=lowest)';
COMMENT ON COLUMN tasks.is_recurring IS 'Whether this is a recurring task';
COMMENT ON COLUMN tasks.recurrence_pattern IS 'Recurrence pattern: daily, weekly, monthly, custom';
COMMENT ON COLUMN tasks.parent_task_id IS 'For recurring tasks, reference to the parent task';
COMMENT ON COLUMN tasks.result_notes IS 'Notes about the task result/outcome';
COMMENT ON COLUMN tasks.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN tasks.updated_at IS 'Record last update timestamp';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS tasks_updated_at ON tasks;
CREATE TRIGGER tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_tasks_customer_id ON tasks(customer_id);
CREATE INDEX IF NOT EXISTS idx_tasks_invoice_id ON tasks(invoice_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to_user_id);

COMMIT;
