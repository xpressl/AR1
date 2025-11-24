-- Migration: 001_create_users
-- Description: Create users table for AR Control Hub authentication and authorization
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- USERS TABLE
-- Purpose: Stores user accounts for AR specialists, managers, sales reps, etc.
-- ============================================================================

BEGIN;

-- Create enum type for user roles
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM (
        'ar_specialist',
        'ar_manager',
        'sales_rep',
        'inside_sales',
        'owner',
        'admin'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Authentication fields
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,

    -- Profile information
    full_name VARCHAR(255),
    role VARCHAR(30) NOT NULL CHECK (role IN ('ar_specialist', 'ar_manager', 'sales_rep', 'inside_sales', 'owner', 'admin')),

    -- Organization assignment
    branch_id VARCHAR(50),

    -- Account status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Session tracking
    last_login_at TIMESTAMP WITH TIME ZONE NULL,

    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Constraints
    CONSTRAINT users_username_length CHECK (LENGTH(username) >= 3),
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Add table comment
COMMENT ON TABLE users IS 'User accounts for AR Control Hub - includes AR specialists, managers, sales reps, and owners';

-- Add column comments
COMMENT ON COLUMN users.id IS 'Unique identifier for the user';
COMMENT ON COLUMN users.username IS 'Unique username for login';
COMMENT ON COLUMN users.email IS 'Unique email address for login and notifications';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password';
COMMENT ON COLUMN users.full_name IS 'User display name';
COMMENT ON COLUMN users.role IS 'User role: ar_specialist, ar_manager, sales_rep, inside_sales, owner, admin';
COMMENT ON COLUMN users.branch_id IS 'Branch/location assignment for filtering';
COMMENT ON COLUMN users.is_active IS 'Whether the user account is active';
COMMENT ON COLUMN users.last_login_at IS 'Timestamp of last successful login';
COMMENT ON COLUMN users.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN users.updated_at IS 'Record last update timestamp';

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS users_updated_at ON users;
CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create basic indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_branch_id ON users(branch_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

COMMIT;
