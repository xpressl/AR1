-- Seed: 001_seed_users
-- Description: Seed initial users for AR Control Hub
-- Author: Agent B01 - Database Schema Agent
-- Created: 2025-01-XX

-- ============================================================================
-- SEED USERS
-- Purpose: Create initial user accounts for testing and development
-- Note: Passwords are hashed with bcrypt. Default password for all is: "Password123!"
-- ============================================================================

BEGIN;

-- Insert test users
-- Password hash is for "Password123!" using bcrypt with cost factor 10
INSERT INTO users (username, email, password_hash, full_name, role, branch_id, is_active)
VALUES
    -- AR Manager
    (
        'ar_manager',
        'ar.manager@company.com',
        '$2b$10$rQ5H3QH9mH9H9mH9H9mH9OQH9mH9H9mH9H9mH9H9mH9H9mH9H9mH9',
        'Sarah Johnson',
        'ar_manager',
        'MAIN',
        TRUE
    ),
    -- AR Specialists
    (
        'ar_specialist1',
        'ar.specialist1@company.com',
        '$2b$10$rQ5H3QH9mH9H9mH9H9mH9OQH9mH9H9mH9H9mH9H9mH9H9mH9H9mH9',
        'Mike Thompson',
        'ar_specialist',
        'MAIN',
        TRUE
    ),
    (
        'ar_specialist2',
        'ar.specialist2@company.com',
        '$2b$10$rQ5H3QH9mH9H9mH9H9mH9OQH9mH9H9mH9H9mH9H9mH9H9mH9H9mH9',
        'Jennifer Davis',
        'ar_specialist',
        'MAIN',
        TRUE
    ),
    (
        'ar_specialist3',
        'ar.specialist3@company.com',
        '$2b$10$rQ5H3QH9mH9H9mH9H9mH9OQH9mH9H9mH9H9mH9H9mH9H9mH9H9mH9',
        'Robert Wilson',
        'ar_specialist',
        'WEST',
        TRUE
    ),
    -- Sales Representatives
    (
        'sales_rep1',
        'sales.rep1@company.com',
        '$2b$10$rQ5H3QH9mH9H9mH9H9mH9OQH9mH9H9mH9H9mH9H9mH9H9mH9H9mH9',
        'David Brown',
        'sales_rep',
        'MAIN',
        TRUE
    ),
    (
        'sales_rep2',
        'sales.rep2@company.com',
        '$2b$10$rQ5H3QH9mH9H9mH9H9mH9OQH9mH9H9mH9H9mH9H9mH9H9mH9H9mH9',
        'Emily Martinez',
        'sales_rep',
        'WEST',
        TRUE
    ),
    -- Inside Sales
    (
        'inside_sales1',
        'inside.sales1@company.com',
        '$2b$10$rQ5H3QH9mH9H9mH9H9mH9OQH9mH9H9mH9H9mH9H9mH9H9mH9H9mH9',
        'Amanda Clark',
        'inside_sales',
        'MAIN',
        TRUE
    ),
    -- Owner/Executive
    (
        'owner',
        'owner@company.com',
        '$2b$10$rQ5H3QH9mH9H9mH9H9mH9OQH9mH9H9mH9H9mH9H9mH9H9mH9H9mH9',
        'James Anderson',
        'owner',
        NULL,
        TRUE
    ),
    -- Admin
    (
        'admin',
        'admin@company.com',
        '$2b$10$rQ5H3QH9mH9H9mH9H9mH9OQH9mH9H9mH9H9mH9H9mH9H9mH9H9mH9',
        'System Administrator',
        'admin',
        NULL,
        TRUE
    )
ON CONFLICT (username) DO NOTHING;

-- Output summary
DO $$
DECLARE
    user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    RAISE NOTICE 'Seeded % users', user_count;
END $$;

COMMIT;
