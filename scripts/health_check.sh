#!/bin/bash
#
# AR Control Hub - Health Check Script
#
# This script monitors the health of all AR Control Hub components.
# Configured to run every 5 minutes via cron.
#
# Checks:
#   1. Backend API health endpoint
#   2. Frontend availability
#   3. Database connectivity
#   4. Disk space usage
#   5. Service status
#
# Exit codes:
#   0 = OK (all healthy)
#   1 = WARNING (non-critical issues)
#   2 = CRITICAL (service down or major issue)
#
# Usage:
#   ./scripts/health_check.sh
#

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
CRITICAL_DISK_USAGE=90
WARNING_DISK_USAGE=80

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Status tracking
CRITICAL_COUNT=0
WARNING_COUNT=0
OK_COUNT=0

# Load environment variables if available
if [ -f "/opt/ar-control-hub/.env.production" ]; then
    export $(grep -v '^#' /opt/ar-control-hub/.env.production | grep -v '^$' | xargs)
fi

# Parse database URL
DB_URL_CLEAN=$(echo "$DATABASE_URL" | sed 's/postgresql+asyncpg/postgresql/' | sed 's/postgresql+psycopg2/postgresql/')
DB_USER=$(echo "$DB_URL_CLEAN" | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASSWORD=$(echo "$DB_URL_CLEAN" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_HOST=$(echo "$DB_URL_CLEAN" | sed -n 's|.*@\([^:]*\):.*|\1|p')
DB_NAME=$(echo "$DB_URL_CLEAN" | sed -n 's|.*/\([^?]*\).*|\1|p')

# Defaults
DB_HOST=${DB_HOST:-localhost}
DB_NAME=${DB_NAME:-ar_control_hub_prod}

# ============================================================
# Health Check Functions
# ============================================================

check_backend() {
    echo -n "Backend API... "

    # Check if backend responds to health endpoint
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health 2>/dev/null)

    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}OK${NC} (HTTP $RESPONSE)"
        ((OK_COUNT++))
        return 0
    elif [ -z "$RESPONSE" ] || [ "$RESPONSE" = "000" ]; then
        echo -e "${RED}CRITICAL${NC} - Not responding"
        ((CRITICAL_COUNT++))
        return 2
    else
        echo -e "${YELLOW}WARNING${NC} (HTTP $RESPONSE)"
        ((WARNING_COUNT++))
        return 1
    fi
}

check_frontend() {
    echo -n "Frontend... "

    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL 2>/dev/null)

    if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "304" ]; then
        echo -e "${GREEN}OK${NC} (HTTP $RESPONSE)"
        ((OK_COUNT++))
        return 0
    elif [ -z "$RESPONSE" ] || [ "$RESPONSE" = "000" ]; then
        echo -e "${RED}CRITICAL${NC} - Not responding"
        ((CRITICAL_COUNT++))
        return 2
    else
        echo -e "${YELLOW}WARNING${NC} (HTTP $RESPONSE)"
        ((WARNING_COUNT++))
        return 1
    fi
}

check_database() {
    echo -n "Database... "

    export PGPASSWORD=$DB_PASSWORD

    if psql -U $DB_USER -h $DB_HOST -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        ((OK_COUNT++))
        unset PGPASSWORD
        return 0
    else
        echo -e "${RED}CRITICAL${NC} - Cannot connect"
        ((CRITICAL_COUNT++))
        unset PGPASSWORD
        return 2
    fi
}

check_disk_space() {
    echo -n "Disk Space... "

    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ "$DISK_USAGE" -ge "$CRITICAL_DISK_USAGE" ]; then
        echo -e "${RED}CRITICAL${NC} - ${DISK_USAGE}% used (threshold: ${CRITICAL_DISK_USAGE}%)"
        ((CRITICAL_COUNT++))
        return 2
    elif [ "$DISK_USAGE" -ge "$WARNING_DISK_USAGE" ]; then
        echo -e "${YELLOW}WARNING${NC} - ${DISK_USAGE}% used (threshold: ${WARNING_DISK_USAGE}%)"
        ((WARNING_COUNT++))
        return 1
    else
        echo -e "${GREEN}OK${NC} - ${DISK_USAGE}% used"
        ((OK_COUNT++))
        return 0
    fi
}

check_backend_service() {
    echo -n "Backend Service (systemd)... "

    if systemctl is-active --quiet ar-backend; then
        echo -e "${GREEN}ACTIVE${NC}"
        ((OK_COUNT++))
        return 0
    else
        echo -e "${RED}CRITICAL${NC} - Service not running"
        ((CRITICAL_COUNT++))
        return 2
    fi
}

check_frontend_service() {
    echo -n "Frontend Service (systemd)... "

    if systemctl is-active --quiet ar-frontend; then
        echo -e "${GREEN}ACTIVE${NC}"
        ((OK_COUNT++))
        return 0
    else
        echo -e "${RED}CRITICAL${NC} - Service not running"
        ((CRITICAL_COUNT++))
        return 2
    fi
}

check_postgresql_service() {
    echo -n "PostgreSQL Service... "

    if systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}ACTIVE${NC}"
        ((OK_COUNT++))
        return 0
    else
        echo -e "${RED}CRITICAL${NC} - Service not running"
        ((CRITICAL_COUNT++))
        return 2
    fi
}

check_nginx_service() {
    echo -n "Nginx Service... "

    if systemctl is-active --quiet nginx 2>/dev/null; then
        echo -e "${GREEN}ACTIVE${NC}"
        ((OK_COUNT++))
        return 0
    else
        echo -e "${YELLOW}WARNING${NC} - Service not running (may not be configured yet)"
        ((WARNING_COUNT++))
        return 1
    fi
}

# ============================================================
# Main Health Check
# ============================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AR Control Hub - Health Check"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run all checks
check_postgresql_service
check_backend_service
check_frontend_service
check_nginx_service
check_database
check_backend
check_frontend
check_disk_space

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Summary
TOTAL_CHECKS=$((OK_COUNT + WARNING_COUNT + CRITICAL_COUNT))

if [ $CRITICAL_COUNT -gt 0 ]; then
    echo -e "${RED}  ✗ CRITICAL: $CRITICAL_COUNT critical issue(s) found${NC}"
    echo -e "  Summary: $OK_COUNT OK, $WARNING_COUNT WARNING, $CRITICAL_COUNT CRITICAL (Total: $TOTAL_CHECKS)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Alert (configure your alerting mechanism)
    # Example: mail -s "AR Control Hub CRITICAL" admin@company.com <<< "Critical health check failures detected"

    exit 2
elif [ $WARNING_COUNT -gt 0 ]; then
    echo -e "${YELLOW}  ⚠ WARNING: $WARNING_COUNT warning(s) found${NC}"
    echo -e "  Summary: $OK_COUNT OK, $WARNING_COUNT WARNING, $CRITICAL_COUNT CRITICAL (Total: $TOTAL_CHECKS)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    exit 1
else
    echo -e "${GREEN}  ✓ ALL HEALTHY: All $TOTAL_CHECKS checks passed${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    exit 0
fi
