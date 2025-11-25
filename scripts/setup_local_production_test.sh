#!/bin/bash
#
# AR Control Hub - Local Production Test Environment Setup
#
# This script sets up a local environment that simulates production
# for testing deployment scripts and procedures.
#
# Usage:
#   ./scripts/setup_local_production_test.sh
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}  AR Control Hub - Local Production Test Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
APP_DIR="/home/user/AR1"
TEST_DB_NAME="ar_control_hub_test_prod"
TEST_DB_USER="ar_test_admin"
TEST_DB_PASSWORD="test_password_123"

cd $APP_DIR

echo -e "${YELLOW}[1/10] Checking Prerequisites${NC}"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${RED}PostgreSQL is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ PostgreSQL installed${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Python 3 installed${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Node.js installed${NC}"

echo ""
echo -e "${YELLOW}[2/10] Creating Test Production Database${NC}"

# Drop database if exists (for clean slate)
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${TEST_DB_NAME};" 2>/dev/null || true

# Create database
sudo -u postgres psql -c "CREATE DATABASE ${TEST_DB_NAME};" || {
    echo -e "${RED}Failed to create database${NC}"
    exit 1
}
echo -e "${GREEN}  ✓ Database '${TEST_DB_NAME}' created${NC}"

# Create user if not exists
sudo -u postgres psql -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '${TEST_DB_USER}') THEN CREATE USER ${TEST_DB_USER} WITH PASSWORD '${TEST_DB_PASSWORD}'; END IF; END \$\$;" || {
    echo -e "${RED}Failed to create user${NC}"
    exit 1
}
echo -e "${GREEN}  ✓ User '${TEST_DB_USER}' created${NC}"

# Grant permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${TEST_DB_NAME} TO ${TEST_DB_USER};" || {
    echo -e "${RED}Failed to grant permissions${NC}"
    exit 1
}

sudo -u postgres psql -d ${TEST_DB_NAME} -c "GRANT ALL ON SCHEMA public TO ${TEST_DB_USER};" || true

echo -e "${GREEN}  ✓ Permissions granted${NC}"

echo ""
echo -e "${YELLOW}[3/10] Creating Test Production Environment File${NC}"

# Create .env.test_production
cat > .env.test_production <<EOF
# ==================================================================
# AR Control Hub - Test Production Environment
# ==================================================================
# This is a LOCAL test environment that simulates production
# DO NOT use these settings in actual production!
# ==================================================================

# Database
DATABASE_URL=postgresql+asyncpg://${TEST_DB_USER}:${TEST_DB_PASSWORD}@localhost:5432/${TEST_DB_NAME}

# API Configuration
ENVIRONMENT=test_production
API_HOST=0.0.0.0
API_PORT=8001
API_URL=http://localhost:8001

# Security (test values)
JWT_SECRET_KEY=test_jwt_secret_key_for_local_testing_only_do_not_use_in_production_12345678901234567890
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Email (test mode - don't actually send)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=test
SMTP_PASSWORD=test
SMTP_FROM_EMAIL=test@localhost
SMTP_FROM_NAME=AR Control Hub Test

# Feature Flags
ENABLE_EMAIL_NOTIFICATIONS=false
ENABLE_DAILY_DIGEST=false
ENABLE_EPICOR_IMPORT=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=/tmp/ar-test-prod/app.log

# Testing
TEST_MODE=true
EOF

chmod 600 .env.test_production
echo -e "${GREEN}  ✓ .env.test_production created${NC}"

echo ""
echo -e "${YELLOW}[4/10] Creating Test Log Directories${NC}"

mkdir -p /tmp/ar-test-prod
mkdir -p /tmp/ar-test-backups
mkdir -p /tmp/ar-test-exports

echo -e "${GREEN}  ✓ Log directories created${NC}"

echo ""
echo -e "${YELLOW}[5/10] Setting Up Python Virtual Environment${NC}"

# Create venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}  ✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}  ✓ Virtual environment exists${NC}"
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo -e "${GREEN}  ✓ Dependencies installed${NC}"

echo ""
echo -e "${YELLOW}[6/10] Running Database Migrations${NC}"

# Export environment variables
export $(grep -v '^#' .env.test_production | xargs)

# Run migrations
alembic upgrade head

echo -e "${GREEN}  ✓ Migrations completed${NC}"

echo ""
echo -e "${YELLOW}[7/10] Creating Test Admin User${NC}"

# Create admin user for testing
python scripts/create_admin_user.py \
    --email admin@test.local \
    --username admin_test \
    --password "TestAdmin123!@#" \
    --full-name "Test Administrator" \
    --database-url "postgresql+asyncpg://${TEST_DB_USER}:${TEST_DB_PASSWORD}@localhost:5432/${TEST_DB_NAME}" || {
    echo -e "${YELLOW}  ⚠ Admin user may already exist${NC}"
}

echo ""
echo -e "${YELLOW}[8/10] Seeding Test Data${NC}"

# Seed with demo data
python scripts/seed_demo_data.py --scenario demo || {
    echo -e "${YELLOW}  ⚠ Demo data seeding skipped or failed${NC}"
}

echo ""
echo -e "${YELLOW}[9/10] Testing Backend Startup${NC}"

# Start backend in background for testing
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8001 > /tmp/ar-test-prod/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo -n "  Waiting for backend to start"
for i in {1..30}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}  ✓ Backend started successfully${NC}"
        break
    fi
    echo -n "."
    sleep 1

    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${RED}  ✗ Backend failed to start${NC}"
        echo "  Check logs: tail -f /tmp/ar-test-prod/backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
done

# Stop backend after test
kill $BACKEND_PID 2>/dev/null || true
sleep 2

echo ""
echo -e "${YELLOW}[10/10] Creating Test Scripts${NC}"

# Create start script
cat > scripts/start_test_prod.sh <<'EOFSCRIPT'
#!/bin/bash
# Start test production environment

cd /home/user/AR1
source venv/bin/activate
export $(grep -v '^#' .env.test_production | xargs)

echo "Starting test production backend..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
EOFSCRIPT

chmod +x scripts/start_test_prod.sh
echo -e "${GREEN}  ✓ start_test_prod.sh created${NC}"

# Create stop script
cat > scripts/stop_test_prod.sh <<'EOFSCRIPT'
#!/bin/bash
# Stop test production environment

echo "Stopping test production backend..."
pkill -f "uvicorn src.api.main:app.*8001" || echo "No backend process found"
echo "Stopped."
EOFSCRIPT

chmod +x scripts/stop_test_prod.sh
echo -e "${GREEN}  ✓ stop_test_prod.sh created${NC}"

# Create test health check script
cat > scripts/test_health_check.sh <<'EOFSCRIPT'
#!/bin/bash
# Test health check in local production environment

export DATABASE_URL="postgresql+asyncpg://ar_test_admin:test_password_123@localhost:5432/ar_control_hub_test_prod"

cd /home/user/AR1
./scripts/health_check.sh
EOFSCRIPT

chmod +x scripts/test_health_check.sh
echo -e "${GREEN}  ✓ test_health_check.sh created${NC}"

# Create test backup script
cat > scripts/test_backup.sh <<'EOFSCRIPT'
#!/bin/bash
# Test backup in local production environment

export DATABASE_URL="postgresql+asyncpg://ar_test_admin:test_password_123@localhost:5432/ar_control_hub_test_prod"
export BACKUP_DIR="/tmp/ar-test-backups"
export LOG_FILE="/tmp/ar-test-prod/backup.log"

cd /home/user/AR1

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Running test backup..."
./scripts/backup_database.sh
echo "Backup completed. Check: ls -lh $BACKUP_DIR"
EOFSCRIPT

chmod +x scripts/test_backup.sh
echo -e "${GREEN}  ✓ test_backup.sh created${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}  ✅ Test Production Environment Setup Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Environment Details:"
echo "   Database: ${TEST_DB_NAME}"
echo "   User: ${TEST_DB_USER}"
echo "   Backend Port: 8001"
echo "   Log Dir: /tmp/ar-test-prod/"
echo "   Backup Dir: /tmp/ar-test-backups/"
echo ""
echo "🚀 Quick Start Commands:"
echo "   Start Backend:    ./scripts/start_test_prod.sh"
echo "   Stop Backend:     ./scripts/stop_test_prod.sh"
echo "   Health Check:     ./scripts/test_health_check.sh"
echo "   Test Backup:      ./scripts/test_backup.sh"
echo ""
echo "🔐 Test Admin Credentials:"
echo "   Email: admin@test.local"
echo "   Password: TestAdmin123!@#"
echo ""
echo "🧪 Test APIs:"
echo "   Health:     curl http://localhost:8001/health"
echo "   Dashboard:  curl http://localhost:8001/api/v1/dashboard/summary"
echo "   API Docs:   http://localhost:8001/docs"
echo ""
echo "📊 Database Access:"
echo "   psql -U ${TEST_DB_USER} -d ${TEST_DB_NAME}"
echo "   Password: ${TEST_DB_PASSWORD}"
echo ""
echo "🧹 Cleanup (when done testing):"
echo "   sudo -u postgres psql -c \"DROP DATABASE ${TEST_DB_NAME};\""
echo "   rm -rf /tmp/ar-test-prod /tmp/ar-test-backups /tmp/ar-test-exports"
echo ""
