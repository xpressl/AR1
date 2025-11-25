#!/bin/bash
#
# AR Control Hub - Demo Environment Verification Script
#
# This script verifies that the demo environment is ready for presentation.
# Run this 1 hour before the demo to catch any issues early.
#
# Usage:
#   ./scripts/verify_demo_environment.sh
#

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}  AR Control Hub - Demo Environment Verification${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 Running comprehensive environment checks..."
echo ""

# Helper function for test results
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ============================================================
# TEST 1: Database Connectivity
# ============================================================
echo -e "${YELLOW}[1/12] Database Connectivity${NC}"

# Check if PostgreSQL is running
if pg_isready -q; then
    pass "PostgreSQL server is running"
else
    fail "PostgreSQL server is not running"
    echo "   Fix: sudo systemctl start postgresql"
fi

# Check if ar_demo database exists
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw ar_demo; then
    pass "Database 'ar_demo' exists"
else
    fail "Database 'ar_demo' not found"
    echo "   Fix: psql -U postgres -c 'CREATE DATABASE ar_demo;'"
fi

# Check database connectivity with credentials
if PGPASSWORD=ar_dev_password psql -U ar_user -d ar_demo -c "SELECT 1;" > /dev/null 2>&1; then
    pass "Database connection successful (ar_user credentials)"
else
    fail "Cannot connect to ar_demo database"
    echo "   Fix: Check DATABASE_URL in .env file"
fi

echo ""

# ============================================================
# TEST 2: Database Schema
# ============================================================
echo -e "${YELLOW}[2/12] Database Schema${NC}"

# Check if tables exist
REQUIRED_TABLES=("customers" "invoices" "payments" "users" "notes" "tasks" "alerts" "notifications")
TABLES_FOUND=$(PGPASSWORD=ar_dev_password psql -U ar_user -d ar_demo -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';" | tr -d ' ')

for table in "${REQUIRED_TABLES[@]}"; do
    if echo "$TABLES_FOUND" | grep -qw "$table"; then
        pass "Table '$table' exists"
    else
        fail "Table '$table' not found"
        echo "   Fix: alembic upgrade head"
    fi
done

echo ""

# ============================================================
# TEST 3: Demo Data
# ============================================================
echo -e "${YELLOW}[3/12] Demo Data${NC}"

# Count customers
CUSTOMER_COUNT=$(PGPASSWORD=ar_dev_password psql -U ar_user -d ar_demo -t -c "SELECT COUNT(*) FROM customers;" | tr -d ' ')
if [ "$CUSTOMER_COUNT" -ge 40 ]; then
    pass "Customers: $CUSTOMER_COUNT (expected ~50)"
elif [ "$CUSTOMER_COUNT" -gt 0 ]; then
    warn "Customers: $CUSTOMER_COUNT (expected ~50, may need more data)"
else
    fail "Customers: 0 (no demo data)"
    echo "   Fix: python scripts/seed_demo_data.py --scenario demo"
fi

# Count invoices
INVOICE_COUNT=$(PGPASSWORD=ar_dev_password psql -U ar_user -d ar_demo -t -c "SELECT COUNT(*) FROM invoices;" | tr -d ' ')
if [ "$INVOICE_COUNT" -ge 150 ]; then
    pass "Invoices: $INVOICE_COUNT (expected ~200)"
elif [ "$INVOICE_COUNT" -gt 0 ]; then
    warn "Invoices: $INVOICE_COUNT (expected ~200, may need more data)"
else
    fail "Invoices: 0 (no demo data)"
    echo "   Fix: python scripts/seed_demo_data.py --scenario demo"
fi

# Check total AR balance
TOTAL_AR=$(PGPASSWORD=ar_dev_password psql -U ar_user -d ar_demo -t -c "SELECT COALESCE(SUM(open_balance), 0) FROM invoices WHERE status = 'Open';" | tr -d ' ')
TOTAL_AR_INT=$(echo "$TOTAL_AR" | cut -d '.' -f 1)

if [ "$TOTAL_AR_INT" -ge 1000000 ]; then
    pass "Total AR: \$${TOTAL_AR_INT} (expected ~\$1.2M)"
elif [ "$TOTAL_AR_INT" -gt 0 ]; then
    warn "Total AR: \$${TOTAL_AR_INT} (expected ~\$1.2M, seems low)"
else
    fail "Total AR: \$0 (no open invoices)"
    echo "   Fix: python scripts/seed_demo_data.py --scenario demo"
fi

# Count users
USER_COUNT=$(PGPASSWORD=ar_dev_password psql -U ar_user -d ar_demo -t -c "SELECT COUNT(*) FROM users;" | tr -d ' ')
if [ "$USER_COUNT" -ge 3 ]; then
    pass "Users: $USER_COUNT (expected 3-4)"
else
    fail "Users: $USER_COUNT (expected at least 3 demo users)"
    echo "   Fix: python scripts/seed_demo_data.py --scenario demo"
fi

echo ""

# ============================================================
# TEST 4: Demo User Accounts
# ============================================================
echo -e "${YELLOW}[4/12] Demo User Accounts${NC}"

# Check if demo users exist
DEMO_USERS=("sarah.martinez@company.com" "michael.chen@company.com" "admin@company.com")
for email in "${DEMO_USERS[@]}"; do
    if PGPASSWORD=ar_dev_password psql -U ar_user -d ar_demo -t -c "SELECT 1 FROM users WHERE email = '$email';" | grep -q 1; then
        pass "Demo user '$email' exists"
    else
        fail "Demo user '$email' not found"
        echo "   Fix: python scripts/seed_demo_data.py --scenario demo"
    fi
done

echo ""

# ============================================================
# TEST 5: Backend Server
# ============================================================
echo -e "${YELLOW}[5/12] Backend Server${NC}"

# Check if backend process is running
if pgrep -f "uvicorn src.api.main:app" > /dev/null; then
    pass "Backend process is running"
else
    fail "Backend process not found"
    echo "   Fix: uvicorn src.api.main:app --host 0.0.0.0 --port 8000"
fi

# Check if backend is responding on port 8000
if nc -z localhost 8000 2>/dev/null; then
    pass "Backend listening on port 8000"
else
    fail "Backend not listening on port 8000"
    echo "   Fix: Check if backend started successfully"
fi

# Check backend health endpoint
HEALTH_CHECK=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    pass "Backend health check: OK"
else
    fail "Backend health check failed"
    echo "   Response: $HEALTH_CHECK"
    echo "   Fix: Check logs/demo_backend.log"
fi

# Check API docs endpoint
if curl -s http://localhost:8000/docs -o /dev/null -w "%{http_code}" 2>/dev/null | grep -q "200"; then
    pass "API documentation accessible"
else
    warn "API documentation not accessible (may not be critical)"
fi

echo ""

# ============================================================
# TEST 6: Frontend Server
# ============================================================
echo -e "${YELLOW}[6/12] Frontend Server${NC}"

# Check if frontend process is running
if pgrep -f "npm.*dev" > /dev/null || pgrep -f "next.*dev" > /dev/null; then
    pass "Frontend process is running"
else
    fail "Frontend process not found"
    echo "   Fix: npm run dev"
fi

# Check if frontend is responding on port 3000
if nc -z localhost 3000 2>/dev/null; then
    pass "Frontend listening on port 3000"
else
    fail "Frontend not listening on port 3000"
    echo "   Fix: Check if frontend started successfully"
fi

# Check if frontend homepage loads
FRONTEND_CHECK=$(curl -s http://localhost:3000 -o /dev/null -w "%{http_code}" 2>/dev/null || echo "000")
if [ "$FRONTEND_CHECK" = "200" ] || [ "$FRONTEND_CHECK" = "304" ]; then
    pass "Frontend homepage loads (HTTP $FRONTEND_CHECK)"
else
    fail "Frontend homepage not loading (HTTP $FRONTEND_CHECK)"
    echo "   Fix: Check logs/demo_frontend.log"
fi

echo ""

# ============================================================
# TEST 7: API Endpoints
# ============================================================
echo -e "${YELLOW}[7/12] Critical API Endpoints${NC}"

# Test dashboard endpoint
DASHBOARD_RESPONSE=$(curl -s http://localhost:8000/api/v1/dashboard/summary 2>/dev/null || echo "{}")
if echo "$DASHBOARD_RESPONSE" | grep -q "total_ar"; then
    pass "Dashboard API endpoint working"
else
    fail "Dashboard API endpoint not working"
    echo "   Response: $DASHBOARD_RESPONSE"
fi

# Test customers endpoint
CUSTOMERS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/customers?skip=0&limit=5" 2>/dev/null || echo "[]")
if echo "$CUSTOMERS_RESPONSE" | grep -q "\["; then
    pass "Customers API endpoint working"
else
    fail "Customers API endpoint not working"
fi

# Test analytics endpoint (cash forecast)
FORECAST_RESPONSE=$(curl -s http://localhost:8000/api/v1/analytics/cash-forecast 2>/dev/null || echo "{}")
if echo "$FORECAST_RESPONSE" | grep -q "weeks\|forecast"; then
    pass "Cash forecast API endpoint working"
else
    warn "Cash forecast API may have issues (check implementation)"
fi

echo ""

# ============================================================
# TEST 8: Python Dependencies
# ============================================================
echo -e "${YELLOW}[8/12] Python Dependencies${NC}"

# Check critical Python packages
REQUIRED_PACKAGES=("fastapi" "sqlalchemy" "asyncpg" "pydantic" "faker" "alembic")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if pip show "$package" > /dev/null 2>&1; then
        pass "Python package '$package' installed"
    else
        fail "Python package '$package' not installed"
        echo "   Fix: pip install $package"
    fi
done

echo ""

# ============================================================
# TEST 9: Node Dependencies
# ============================================================
echo -e "${YELLOW}[9/12] Node Dependencies${NC}"

# Check if node_modules exists
if [ -d "node_modules" ]; then
    pass "node_modules directory exists"
else
    fail "node_modules directory not found"
    echo "   Fix: npm install"
fi

# Check package.json exists
if [ -f "package.json" ]; then
    pass "package.json exists"
else
    fail "package.json not found"
fi

# Check if Next.js is installed
if npm list next > /dev/null 2>&1; then
    pass "Next.js installed"
else
    fail "Next.js not installed"
    echo "   Fix: npm install"
fi

echo ""

# ============================================================
# TEST 10: Environment Variables
# ============================================================
echo -e "${YELLOW}[10/12] Environment Variables${NC}"

# Check if .env file exists
if [ -f ".env" ]; then
    pass ".env file exists"

    # Check critical environment variables in .env
    if grep -q "DATABASE_URL" .env; then
        pass ".env contains DATABASE_URL"
    else
        fail ".env missing DATABASE_URL"
    fi

    if grep -q "JWT_SECRET_KEY" .env; then
        pass ".env contains JWT_SECRET_KEY"
    else
        warn ".env missing JWT_SECRET_KEY (may use default)"
    fi
else
    warn ".env file not found (may use defaults)"
fi

echo ""

# ============================================================
# TEST 11: Log Files
# ============================================================
echo -e "${YELLOW}[11/12] Log Files${NC}"

# Check if logs directory exists
if [ -d "logs" ]; then
    pass "logs directory exists"
else
    warn "logs directory not found (will be created on first run)"
    mkdir -p logs
fi

# Check backend log
if [ -f "logs/demo_backend.log" ]; then
    pass "Backend log file exists"

    # Check for recent errors
    RECENT_ERRORS=$(tail -50 logs/demo_backend.log | grep -i "error" | wc -l)
    if [ "$RECENT_ERRORS" -gt 0 ]; then
        warn "Found $RECENT_ERRORS recent errors in backend log"
        echo "   Review: tail -50 logs/demo_backend.log"
    else
        pass "No recent errors in backend log"
    fi
else
    warn "Backend log file not found (will be created when backend starts)"
fi

# Check frontend log
if [ -f "logs/demo_frontend.log" ]; then
    pass "Frontend log file exists"
else
    warn "Frontend log file not found (will be created when frontend starts)"
fi

echo ""

# ============================================================
# TEST 12: Demo Materials
# ============================================================
echo -e "${YELLOW}[12/12] Demo Materials${NC}"

# Check if demo guide exists
if [ -f "docs/DEMO_GUIDE.md" ]; then
    pass "Demo guide (DEMO_GUIDE.md) exists"
else
    fail "Demo guide not found"
fi

# Check if quick reference exists
if [ -f "docs/DEMO_QUICK_REFERENCE.md" ]; then
    pass "Quick reference card exists"
else
    warn "Quick reference card not found"
fi

# Check if troubleshooting guide exists
if [ -f "docs/DEMO_TROUBLESHOOTING.md" ]; then
    pass "Troubleshooting guide exists"
else
    warn "Troubleshooting guide not found"
fi

# Check if pre-demo checklist exists
if [ -f "docs/PRE_DEMO_CHECKLIST.md" ]; then
    pass "Pre-demo checklist exists"
else
    warn "Pre-demo checklist not found"
fi

# Check if feature summary exists
if [ -f "docs/AR_CONTROL_HUB_FEATURE_SUMMARY.md" ]; then
    pass "Feature summary exists"
else
    warn "Feature summary not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}  Verification Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✓ Passed:${NC}   $PASSED"
echo -e "${YELLOW}⚠ Warnings:${NC} $WARNINGS"
echo -e "${RED}✗ Failed:${NC}   $FAILED"
echo ""

# Final recommendation
if [ "$FAILED" -eq 0 ]; then
    if [ "$WARNINGS" -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  ✓ DEMO ENVIRONMENT READY${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "🎉 All checks passed! Your demo environment is ready."
        echo ""
        echo "📋 Next Steps:"
        echo "   1. Review DEMO_QUICK_REFERENCE.md"
        echo "   2. Practice your presentation"
        echo "   3. Test login to all 3 demo accounts"
        echo "   4. Have DEMO_TROUBLESHOOTING.md handy just in case"
        echo ""
        echo "🚀 You're all set for a great demo!"
    else
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}  ⚠ DEMO ENVIRONMENT READY (WITH WARNINGS)${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "✓ Core functionality is working, but there are some warnings."
        echo "⚠ Review warnings above - they may not be critical."
        echo ""
        echo "Recommendation: Demo should work, but review warnings to be safe."
    fi
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  ✗ DEMO ENVIRONMENT HAS ISSUES${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "❌ $FAILED critical issues found. Please fix before demo."
    echo ""
    echo "📋 Quick Fixes:"
    echo "   • Database issues: Run ./scripts/setup_demo_environment.sh"
    echo "   • Missing data: python scripts/seed_demo_data.py --scenario demo"
    echo "   • Server not running: Check logs/demo_backend.log and logs/demo_frontend.log"
    echo ""
    echo "📖 For detailed troubleshooting, see: docs/DEMO_TROUBLESHOOTING.md"
    echo ""
    exit 1
fi

echo ""
