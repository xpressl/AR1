"""Initial database schema with all models including Phase 4

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for AR Control Hub."""

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('role', sa.String(30), nullable=False),
        sa.Column('branch_id', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_login_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_number', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('contact_name', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('address', sa.String(500)),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(50)),
        sa.Column('zip', sa.String(20)),
        sa.Column('country', sa.String(50), server_default='USA'),
        sa.Column('credit_limit', sa.Numeric(15, 2)),
        sa.Column('payment_terms', sa.String(50)),
        sa.Column('ar_balance', sa.Numeric(15, 2), server_default='0'),
        sa.Column('status', sa.String(20), server_default='Active'),
        sa.Column('last_payment_date', sa.Date()),
        sa.Column('last_invoice_date', sa.Date()),
        sa.Column('salesperson_id', sa.Integer()),
        sa.Column('risk_score', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_number')
    )
    op.create_index('ix_customers_id', 'customers', ['id'])
    op.create_index('ix_customers_customer_number', 'customers', ['customer_number'])
    op.create_index('ix_customers_status', 'customers', ['status'])
    op.create_index('ix_customers_salesperson_id', 'customers', ['salesperson_id'])

    # Invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('amount_paid', sa.Numeric(15, 2), server_default='0'),
        sa.Column('amount_due', sa.Numeric(15, 2), nullable=False),
        sa.Column('status', sa.String(20), server_default='Open'),
        sa.Column('po_number', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number')
    )
    op.create_index('ix_invoices_id', 'invoices', ['id'])
    op.create_index('ix_invoices_customer_id', 'invoices', ['customer_id'])
    op.create_index('ix_invoices_invoice_number', 'invoices', ['invoice_number'])
    op.create_index('ix_invoices_status', 'invoices', ['status'])
    op.create_index('ix_invoices_due_date', 'invoices', ['due_date'])

    # Payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('payment_number', sa.String(50)),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('reference_number', sa.String(100)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by_user_id', sa.Integer()),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payments_id', 'payments', ['id'])
    op.create_index('ix_payments_customer_id', 'payments', ['customer_id'])
    op.create_index('ix_payments_payment_date', 'payments', ['payment_date'])

    # Payment Applications table
    op.create_table(
        'payment_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('amount_applied', sa.Numeric(15, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payment_applications_payment_id', 'payment_applications', ['payment_id'])
    op.create_index('ix_payment_applications_invoice_id', 'payment_applications', ['invoice_id'])

    # Notes table
    op.create_table(
        'notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('note_type', sa.String(50)),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notes_id', 'notes', ['id'])
    op.create_index('ix_notes_customer_id', 'notes', ['customer_id'])
    op.create_index('ix_notes_created_at', 'notes', ['created_at'])

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_user_id', sa.Integer()),
        sa.Column('created_by_user_id', sa.Integer()),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('due_date', sa.Date()),
        sa.Column('status', sa.String(20), server_default='Open'),
        sa.Column('priority', sa.String(20), server_default='Normal'),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_id', 'tasks', ['id'])
    op.create_index('ix_tasks_customer_id', 'tasks', ['customer_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'])

    # Alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), server_default='Low'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default='false'),
        sa.Column('is_resolved', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alerts_id', 'alerts', ['id'])
    op.create_index('ix_alerts_customer_id', 'alerts', ['customer_id'])
    op.create_index('ix_alerts_is_read', 'alerts', ['is_read'])
    op.create_index('ix_alerts_alert_type', 'alerts', ['alert_type'])

    # Disputes table
    op.create_table(
        'disputes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('reason_code', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('disputed_amount', sa.Numeric(15, 2)),
        sa.Column('status', sa.String(20), server_default='Open'),
        sa.Column('assigned_to_user_id', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('resolution_note', sa.Text()),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_disputes_id', 'disputes', ['id'])
    op.create_index('ix_disputes_customer_id', 'disputes', ['customer_id'])
    op.create_index('ix_disputes_invoice_id', 'disputes', ['invoice_id'])
    op.create_index('ix_disputes_status', 'disputes', ['status'])
    op.create_index('ix_disputes_reason_code', 'disputes', ['reason_code'])

    # Email Logs table
    op.create_table(
        'email_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer()),
        sa.Column('recipient', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(500)),
        sa.Column('body', sa.Text()),
        sa.Column('sent_by_user_id', sa.Integer()),
        sa.Column('sent_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('status', sa.String(50), server_default='Sent'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['sent_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_email_logs_id', 'email_logs', ['id'])
    op.create_index('ix_email_logs_customer_id', 'email_logs', ['customer_id'])

    # Import Runs table
    op.create_table(
        'import_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('import_type', sa.String(50), nullable=False),
        sa.Column('filename', sa.String(255)),
        sa.Column('status', sa.String(20), server_default='Pending'),
        sa.Column('records_processed', sa.Integer(), server_default='0'),
        sa.Column('records_created', sa.Integer(), server_default='0'),
        sa.Column('records_updated', sa.Integer(), server_default='0'),
        sa.Column('records_failed', sa.Integer(), server_default='0'),
        sa.Column('error_log', sa.Text()),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('started_by_user_id', sa.Integer()),
        sa.ForeignKeyConstraint(['started_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Credit Holds table
    op.create_table(
        'credit_holds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(200)),
        sa.Column('placed_by_user_id', sa.Integer()),
        sa.Column('placed_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('released_by_user_id', sa.Integer()),
        sa.Column('released_at', sa.DateTime()),
        sa.Column('notes', sa.Text()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['placed_by_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['released_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text()),
        sa.Column('is_read', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('read_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])

    # ========================================
    # Phase 4 Tables
    # ========================================

    # Dispute Attachments table
    op.create_table(
        'dispute_attachments',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('dispute_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer()),
        sa.Column('file_type', sa.String(50)),
        sa.Column('uploaded_by', UUID(as_uuid=True)),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.ForeignKeyConstraint(['dispute_id'], ['disputes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Dispute History table
    op.create_table(
        'dispute_history',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('dispute_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('old_value', sa.Text()),
        sa.Column('new_value', sa.Text()),
        sa.Column('comment', sa.Text()),
        sa.Column('changed_by', UUID(as_uuid=True)),
        sa.Column('changed_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dispute_id'], ['disputes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Email Templates table
    op.create_table(
        'email_templates',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('subject', sa.String(300), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('template_type', sa.String(50), nullable=False),
        sa.Column('category', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_default', sa.Boolean(), server_default='false'),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('available_variables', sa.Text()),
        sa.Column('usage_count', sa.Integer(), server_default='0'),
        sa.Column('last_used_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Template Usage Log table
    op.create_table(
        'template_usage_log',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', sa.Integer()),
        sa.Column('sent_by', UUID(as_uuid=True)),
        sa.Column('sent_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('opened_at', sa.DateTime()),
        sa.Column('clicked_at', sa.DateTime()),
        sa.Column('status', sa.String(50), server_default='sent'),
        sa.Column('recipient_email', sa.String(200)),
        sa.Column('subject_rendered', sa.String(300)),
        sa.Column('email_log_id', sa.Integer()),
        sa.ForeignKeyConstraint(['template_id'], ['email_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sent_by'], ['users.id']),
        sa.ForeignKeyConstraint(['email_log_id'], ['email_logs.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Batch Operations table
    op.create_table(
        'batch_operations',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('operation_type', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('total_records', sa.Integer(), nullable=False),
        sa.Column('processed_records', sa.Integer(), server_default='0'),
        sa.Column('successful_records', sa.Integer(), server_default='0'),
        sa.Column('failed_records', sa.Integer(), server_default='0'),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('initiated_by', UUID(as_uuid=True), nullable=False),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('error_log', sa.Text()),
        sa.Column('result_summary', sa.Text()),
        sa.ForeignKeyConstraint(['initiated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Export History table
    op.create_table(
        'export_history',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('export_type', sa.String(100), nullable=False),
        sa.Column('export_name', sa.String(200)),
        sa.Column('file_format', sa.String(20), nullable=False),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('record_count', sa.Integer()),
        sa.Column('filters', JSONB()),
        sa.Column('exported_by', UUID(as_uuid=True), nullable=False),
        sa.Column('exported_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(50), server_default='completed'),
        sa.Column('expires_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['exported_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop all tables."""
    # Phase 4 tables (drop first due to foreign keys)
    op.drop_table('export_history')
    op.drop_table('batch_operations')
    op.drop_table('template_usage_log')
    op.drop_table('email_templates')
    op.drop_table('dispute_history')
    op.drop_table('dispute_attachments')

    # Core tables
    op.drop_table('notifications')
    op.drop_table('credit_holds')
    op.drop_table('import_runs')
    op.drop_table('email_logs')
    op.drop_table('disputes')
    op.drop_table('alerts')
    op.drop_table('tasks')
    op.drop_table('notes')
    op.drop_table('payment_applications')
    op.drop_table('payments')
    op.drop_table('invoices')
    op.drop_table('customers')
    op.drop_table('users')
