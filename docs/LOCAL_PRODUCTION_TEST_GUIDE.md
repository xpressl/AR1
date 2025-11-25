# AR Control Hub - Local Production Testing Guide

**Purpose:** Test production deployment procedures locally before deploying to actual production server.

---

## Overview

This guide helps you validate all production scripts, configurations, and procedures in a safe local environment before deploying to production.

---

## Prerequisites

### Required Software
- Python 3.11+
- PostgreSQL 14+ (running)
- Node.js 18+
- Git

### System Access
- Sudo/admin access (for testing systemd services)
- PostgreSQL admin access

---

## Test Environment Setup

### Option 1: Full Local Production Simulation (Recommended)

```bash
# 1. Run the automated setup script
./scripts/setup_local_production_test.sh

# This script:
# - Creates test production database (ar_control_hub_test_prod)
# - Sets up test environment file (.env.test_production)
# - Runs migrations
# - Creates test admin user
# - Seeds demo data
# - Tests backend startup
# - Creates helper scripts
```

### Option 2: Manual Setup (If automated script fails)

```bash
# 1. Create test database
psql -U postgres -c "CREATE DATABASE ar_control_hub_test_prod;"
psql -U postgres -c "CREATE USER ar_test_admin WITH PASSWORD 'test_password_123';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ar_control_hub_test_prod TO ar_test_admin;"

# 2. Create test environment file
cp .env.production.template .env.test_production

# Edit .env.test_production with test values:
# DATABASE_URL=postgresql+asyncpg://ar_test_admin:test_password_123@localhost:5432/ar_control_hub_test_prod
# API_PORT=8001
# ENVIRONMENT=test_production

# 3. Run migrations
export $(grep -v '^#' .env.test_production | xargs)
source venv/bin/activate
alembic upgrade head

# 4. Create test admin user
python scripts/create_admin_user.py \
    --email admin@test.local \
    --username admin_test \
    --password "TestAdmin123!@#" \
    --full-name "Test Administrator"

# 5. Seed demo data
python scripts/seed_demo_data.py --scenario demo
```

---

## Testing Production Scripts

### 1. Test Health Check Script

**Purpose:** Verify health_check.sh works correctly

```bash
# Run health check
./scripts/test_health_check.sh

# Expected output:
# ✓ Backend API... OK
# ✓ Frontend... OK
# ✓ Database... OK
# ✓ Disk Space... OK
# ✓ ALL HEALTHY
```

**What to verify:**
- [x] Script runs without errors
- [x] All checks show OK status
- [x] Exit code is 0 (echo $?)
- [x] Output is color-coded correctly

---

### 2. Test Backup Script

**Purpose:** Verify backup_database.sh creates backups correctly

```bash
# Run backup
./scripts/test_backup.sh

# Check backup created
ls -lh /tmp/ar-test-backups/

# Expected output:
# ar_prod_backup_YYYYMMDD_HHMMSS.sql.gz
```

**What to verify:**
- [x] Backup file created
- [x] File is compressed (.gz extension)
- [x] File size is reasonable (> 1KB)
- [x] Backup log updated (/tmp/ar-test-prod/backup.log)
- [x] Old backups are deleted (after 30 days)

**Test backup restore:**
```bash
# Create test restore database
psql -U postgres -c "CREATE DATABASE ar_test_restore;"

# Restore latest backup
LATEST_BACKUP=$(ls -t /tmp/ar-test-backups/*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | psql -U postgres -d ar_test_restore

# Verify data
psql -U postgres -d ar_test_restore -c "SELECT COUNT(*) FROM customers;"

# Cleanup
psql -U postgres -c "DROP DATABASE ar_test_restore;"
```

---

### 3. Test Admin User Creation

**Purpose:** Verify create_admin_user.py works correctly

```bash
# Create another test user
python scripts/create_admin_user.py \
    --email test2@test.local \
    --username test_user2 \
    --password "SecurePassword123!@#" \
    --full-name "Test User 2"

# Expected output:
# ✅ Admin user created successfully!
# User ID: ...
# Email: test2@test.local
```

**What to verify:**
- [x] User created successfully
- [x] Password validation works (rejects weak passwords)
- [x] Duplicate user detection works (try creating same user twice)
- [x] User can log in via API

---

### 4. Test Backend Startup

**Purpose:** Verify backend starts correctly with production config

```bash
# Start backend
./scripts/start_test_prod.sh

# In another terminal, test endpoints
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/dashboard/summary

# Stop backend
./scripts/stop_test_prod.sh
```

**What to verify:**
- [x] Backend starts without errors
- [x] Health endpoint returns 200
- [x] API endpoints work
- [x] Database connections established
- [x] Logs written to /tmp/ar-test-prod/app.log

---

### 5. Test Export Functionality

**Purpose:** Verify export scripts work correctly

```bash
# Start backend
./scripts/start_test_prod.sh

# Test Excel export (in another terminal)
curl -o /tmp/test_export.xlsx \
    "http://localhost:8001/api/v1/export/customers?format=xlsx"

# Verify file created
file /tmp/test_export.xlsx
ls -lh /tmp/test_export.xlsx

# Test CSV export
curl -o /tmp/test_export.csv \
    "http://localhost:8001/api/v1/export/customers?format=csv"

# Stop backend
./scripts/stop_test_prod.sh
```

**What to verify:**
- [x] Export files created
- [x] Files are valid (can be opened)
- [x] Export history recorded in database
- [x] Files auto-expire after 7 days

---

### 6. Test Batch Operations

**Purpose:** Verify batch operations work correctly

```bash
# Start backend
./scripts/start_test_prod.sh

# Test bulk note creation (in another terminal)
curl -X POST http://localhost:8001/api/v1/batch/add-notes \
    -H "Content-Type: application/json" \
    -d '{
        "customer_ids": ["customer-id-1", "customer-id-2"],
        "note_content": "Test bulk note",
        "note_type": "general"
    }'

# Check batch status
curl http://localhost:8001/api/v1/batch/status/{batch_id}

# Stop backend
./scripts/stop_test_prod.sh
```

**What to verify:**
- [x] Batch operation created
- [x] Progress tracking works
- [x] Success/failure counts correct
- [x] Error logging works
- [x] Database records created

---

### 7. Test Deployment Script (Dry Run)

**Purpose:** Verify deploy_production.sh logic without actually deploying

```bash
# Review the deployment script
cat scripts/deploy_production.sh

# Check each step manually:
# - Database migrations (already tested above)
# - Frontend build
# - Service configuration
# - Log rotation
# - Backup setup
```

**Manual step-by-step verification:**

```bash
# 1. Test frontend build
npm run build

# 2. Test systemd service files (syntax only)
cat > /tmp/test-backend.service <<EOF
[Unit]
Description=Test Backend
[Service]
ExecStart=/usr/bin/echo "test"
EOF

systemd-analyze verify /tmp/test-backend.service

# 3. Test log rotation config (syntax only)
cat > /tmp/test-logrotate <<EOF
/tmp/test/*.log {
    daily
    rotate 30
}
EOF

logrotate -d /tmp/test-logrotate

# 4. Test cron job syntax
echo "0 2 * * * /home/user/AR1/scripts/backup_database.sh" | crontab -l
```

---

## Validation Checklist

### Database & Migrations
- [x] Migrations run successfully
- [x] All tables created
- [x] Indexes created
- [x] Foreign keys working
- [x] Sample data loads correctly

### API Functionality
- [x] Health check endpoint works
- [x] Dashboard endpoint returns data
- [x] Customer endpoints work
- [x] Invoice endpoints work
- [x] Reports generate correctly
- [x] Export functions work
- [x] Batch operations work

### Scripts & Automation
- [x] health_check.sh runs successfully
- [x] backup_database.sh creates backups
- [x] create_admin_user.py creates users
- [x] Backup restore works
- [x] Old file cleanup works

### Configuration
- [x] .env.test_production has all required variables
- [x] Database connection works
- [x] CORS configured correctly
- [x] Logging configured
- [x] Error handling works

### Performance
- [x] API response times < 500ms
- [x] Database queries optimized
- [x] No N+1 query issues
- [x] Memory usage reasonable
- [x] No memory leaks

### Security
- [x] JWT authentication works
- [x] Password hashing works
- [x] RBAC permissions enforced
- [x] SQL injection prevention
- [x] XSS prevention (frontend)

---

## Common Issues & Solutions

### Issue: Database connection fails

**Symptoms:**
- "could not connect to database" errors
- Health check fails on database test

**Solutions:**
1. Verify PostgreSQL is running:
   ```bash
   pg_isready
   ```

2. Check DATABASE_URL in .env.test_production

3. Verify user has permissions:
   ```bash
   psql -U ar_test_admin -d ar_control_hub_test_prod -c "SELECT 1;"
   ```

---

### Issue: Migrations fail

**Symptoms:**
- "table already exists" errors
- Alembic version conflicts

**Solutions:**
1. Check current migration version:
   ```bash
   alembic current
   ```

2. Reset database (caution: deletes all data):
   ```bash
   psql -U postgres -c "DROP DATABASE ar_control_hub_test_prod;"
   psql -U postgres -c "CREATE DATABASE ar_control_hub_test_prod;"
   alembic upgrade head
   ```

3. If stuck, downgrade and re-upgrade:
   ```bash
   alembic downgrade base
   alembic upgrade head
   ```

---

### Issue: Backend won't start

**Symptoms:**
- uvicorn exits immediately
- "Address already in use" error

**Solutions:**
1. Check if port 8001 is in use:
   ```bash
   lsof -i :8001
   ```

2. Kill existing process:
   ```bash
   pkill -f "uvicorn.*8001"
   ```

3. Check logs for errors:
   ```bash
   tail -f /tmp/ar-test-prod/app.log
   ```

---

### Issue: Exports fail

**Symptoms:**
- Export endpoints return 500 errors
- "No module named openpyxl" errors

**Solutions:**
1. Verify dependencies installed:
   ```bash
   pip list | grep -E "openpyxl|weasyprint|reportlab"
   ```

2. Install missing dependencies:
   ```bash
   pip install openpyxl weasyprint reportlab Pillow
   ```

3. Check export directory permissions:
   ```bash
   ls -la /tmp/ar-test-exports
   ```

---

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API performance
ab -n 100 -c 10 http://localhost:8001/api/v1/dashboard/summary

# Expected results:
# - Requests per second: > 20
# - Time per request: < 500ms (95th percentile)
# - Failed requests: 0
```

### Database Performance

```bash
# Check slow queries
psql -U ar_test_admin -d ar_control_hub_test_prod -c "
SELECT query, calls, mean_time, max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"

# Expected:
# - No queries > 1000ms mean time
# - Most queries < 100ms
```

---

## Cleanup After Testing

### Remove Test Environment

```bash
# 1. Stop any running processes
./scripts/stop_test_prod.sh

# 2. Drop test database
psql -U postgres -c "DROP DATABASE ar_control_hub_test_prod;"

# 3. Remove test files
rm -rf /tmp/ar-test-prod
rm -rf /tmp/ar-test-backups
rm -rf /tmp/ar-test-exports

# 4. Remove test environment file
rm .env.test_production

# 5. Remove test scripts (optional)
rm scripts/start_test_prod.sh
rm scripts/stop_test_prod.sh
rm scripts/test_health_check.sh
rm scripts/test_backup.sh
```

---

## Next Steps

Once all tests pass:

1. **Review Production Checklist**
   - Read `PRODUCTION_DEPLOYMENT_CHECKLIST.md`
   - Verify all prerequisites met

2. **Prepare Production Server**
   - Provision server with required specs
   - Install prerequisites
   - Configure firewall
   - Obtain SSL certificate

3. **Deploy to Production**
   - Follow `PRODUCTION_DEPLOYMENT_CHECKLIST.md` step-by-step
   - Run `deploy_production.sh` on production server
   - Validate deployment
   - Monitor for 24 hours

4. **Monitor & Maintain**
   - Use `PRODUCTION_RUNBOOK.md` for operations
   - Set up monitoring alerts
   - Schedule regular backups
   - Plan for Phase 5 enhancements

---

## Success Criteria

✅ All tests in this guide pass
✅ No errors in logs
✅ Performance meets targets
✅ Security checks pass
✅ Backup/restore works
✅ Health checks pass
✅ Team trained on procedures

**When all criteria met: Ready for production deployment! 🚀**
