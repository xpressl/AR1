#!/bin/bash
#
# AR Control Hub - Production Readiness Verification
#
# This script verifies that the application is ready for production deployment.
# Run this before deploying to production to catch any issues early.
#
# Usage:
#   ./scripts/verify_production_readiness.sh
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}  AR Control Hub - Production Readiness Verification${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Helper functions
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

# ============================================================
# 1. Code Quality Checks
# ============================================================
echo -e "${YELLOW}[1/12] Code Quality${NC}"

# Check if critical files exist
if [ -f "src/api/main.py" ]; then
    pass "Main API file exists"
else
    fail "Main API file missing"
fi

if [ -f "requirements.txt" ]; then
    pass "requirements.txt exists"
else
    fail "requirements.txt missing"
fi

if [ -f "alembic.ini" ]; then
    pass "Alembic configuration exists"
else
    fail "Alembic configuration missing"
fi

# Check for TODO/FIXME in critical files
TODO_COUNT=$(grep -r "TODO\|FIXME" src/ 2>/dev/null | wc -l || echo "0")
if [ "$TODO_COUNT" -gt 0 ]; then
    warn "Found $TODO_COUNT TODO/FIXME comments (review before production)"
else
    pass "No TODO/FIXME comments found"
fi

echo ""

# ============================================================
# 2. Dependencies Check
# ============================================================
echo -e "${YELLOW}[2/12] Dependencies${NC}"

if [ -f "venv/bin/python" ] || [ -f "venv/bin/python3" ]; then
    pass "Virtual environment exists"
else
    fail "Virtual environment not found"
fi

# Check critical Python packages
CRITICAL_PACKAGES=("fastapi" "sqlalchemy" "alembic" "pydantic" "uvicorn")
for pkg in "${CRITICAL_PACKAGES[@]}"; do
    if pip list 2>/dev/null | grep -qi "^$pkg "; then
        pass "Package '$pkg' installed"
    else
        fail "Package '$pkg' not installed"
    fi
done

# Check Phase 4 packages
PHASE4_PACKAGES=("openpyxl" "weasyprint" "Pillow")
for pkg in "${PHASE4_PACKAGES[@]}"; do
    if pip list 2>/dev/null | grep -qi "^$pkg "; then
        pass "Phase 4 package '$pkg' installed"
    else
        warn "Phase 4 package '$pkg' not installed (needed for exports)"
    fi
done

echo ""

# ============================================================
# 3. Database Models
# ============================================================
echo -e "${YELLOW}[3/12] Database Models${NC}"

# Check if all models are imported
if grep -q "DisputeAttachment" src/models/__init__.py; then
    pass "Phase 4 models imported"
else
    warn "Phase 4 models may not be imported"
fi

# Count total models
MODEL_COUNT=$(grep -c "^from src.models" src/models/__init__.py 2>/dev/null || echo "0")
if [ "$MODEL_COUNT" -ge 18 ]; then
    pass "All models imported ($MODEL_COUNT models)"
else
    warn "Expected 18+ models, found $MODEL_COUNT"
fi

echo ""

# ============================================================
# 4. Database Migrations
# ============================================================
echo -e "${YELLOW}[4/12] Database Migrations${NC}"

# Check if migrations directory exists
if [ -d "alembic/versions" ]; then
    pass "Migrations directory exists"

    MIGRATION_COUNT=$(ls -1 alembic/versions/*.py 2>/dev/null | wc -l)
    if [ "$MIGRATION_COUNT" -gt 0 ]; then
        pass "Found $MIGRATION_COUNT migration files"
    else
        warn "No migration files found"
    fi
else
    fail "Migrations directory not found"
fi

echo ""

# ============================================================
# 5. Configuration Files
# ============================================================
echo -e "${YELLOW}[5/12] Configuration Files${NC}"

if [ -f ".env.production.template" ]; then
    pass ".env.production.template exists"
else
    fail ".env.production.template missing"
fi

if [ -f ".gitignore" ]; then
    if grep -q ".env.production" .gitignore; then
        pass ".env.production in .gitignore"
    else
        fail ".env.production not in .gitignore (security risk!)"
    fi
else
    warn ".gitignore not found"
fi

# Check if .env.production exists (shouldn't be in repo)
if [ -f ".env.production" ]; then
    warn ".env.production exists (ensure it's not committed to git)"
else
    pass ".env.production not in repository (good)"
fi

echo ""

# ============================================================
# 6. Deployment Scripts
# ============================================================
echo -e "${YELLOW}[6/12] Deployment Scripts${NC}"

DEPLOYMENT_SCRIPTS=(
    "scripts/deploy_production.sh"
    "scripts/backup_database.sh"
    "scripts/health_check.sh"
    "scripts/create_admin_user.py"
)

for script in "${DEPLOYMENT_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            pass "$(basename $script) exists and is executable"
        else
            warn "$(basename $script) exists but not executable"
        fi
    else
        fail "$(basename $script) missing"
    fi
done

echo ""

# ============================================================
# 7. Documentation
# ============================================================
echo -e "${YELLOW}[7/12] Documentation${NC}"

REQUIRED_DOCS=(
    "README.md"
    "DEPLOYMENT.md"
    "PRODUCTION_DEPLOYMENT_CHECKLIST.md"
    "PRODUCTION_RUNBOOK.md"
    "QUICKSTART.md"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ] || [ -f "docs/$doc" ]; then
        pass "$doc exists"
    else
        warn "$doc missing"
    fi
done

echo ""

# ============================================================
# 8. API Routes
# ============================================================
echo -e "${YELLOW}[8/12] API Routes${NC}"

# Check critical API route files
API_ROUTES=(
    "src/api/routes/auth.py"
    "src/api/routes/customers.py"
    "src/api/routes/invoices.py"
    "src/api/routes/dashboard.py"
    "src/api/routes/export.py"
    "src/api/routes/batch.py"
)

for route in "${API_ROUTES[@]}"; do
    if [ -f "$route" ]; then
        pass "$(basename $route) exists"
    else
        warn "$(basename $route) missing"
    fi
done

echo ""

# ============================================================
# 9. Services
# ============================================================
echo -e "${YELLOW}[9/12] Services${NC}"

# Check Phase 4 services
SERVICES=(
    "src/services/reports/report_service.py"
    "src/services/export/export_service.py"
    "src/services/batch/batch_service.py"
)

for service in "${SERVICES[@]}"; do
    if [ -f "$service" ]; then
        pass "$(basename $service) exists"
    else
        warn "$(basename $service) missing (Phase 4 feature)"
    fi
done

echo ""

# ============================================================
# 10. Security Checks
# ============================================================
echo -e "${YELLOW}[10/12] Security${NC}"

# Check for hardcoded secrets
HARDCODED_SECRETS=$(grep -r "password.*=.*['\"]" src/ 2>/dev/null | grep -v "# " | wc -l || echo "0")
if [ "$HARDCODED_SECRETS" -eq 0 ]; then
    pass "No hardcoded passwords found in source"
else
    fail "Found $HARDCODED_SECRETS potential hardcoded passwords"
fi

# Check for debug mode
if grep -r "DEBUG.*=.*True" src/ 2>/dev/null | grep -v "#" | grep -q .; then
    fail "DEBUG mode enabled in source code"
else
    pass "DEBUG mode not enabled in source"
fi

# Check for print statements (should use logging)
PRINT_COUNT=$(grep -r "print(" src/ 2>/dev/null | grep -v "# " | wc -l || echo "0")
if [ "$PRINT_COUNT" -gt 10 ]; then
    warn "Found $PRINT_COUNT print statements (should use logging)"
else
    pass "Minimal print statements found ($PRINT_COUNT)"
fi

echo ""

# ============================================================
# 11. Testing
# ============================================================
echo -e "${YELLOW}[11/12] Testing${NC}"

if [ -d "tests" ]; then
    pass "Tests directory exists"

    TEST_COUNT=$(find tests -name "test_*.py" | wc -l)
    if [ "$TEST_COUNT" -gt 0 ]; then
        pass "Found $TEST_COUNT test files"
    else
        warn "No test files found"
    fi
else
    warn "Tests directory not found"
fi

if [ -f "pytest.ini" ]; then
    pass "pytest.ini exists"
else
    warn "pytest.ini missing"
fi

echo ""

# ============================================================
# 12. Frontend Build
# ============================================================
echo -e "${YELLOW}[12/12] Frontend${NC}"

if [ -f "package.json" ]; then
    pass "package.json exists"
else
    warn "package.json not found"
fi

if [ -d "node_modules" ]; then
    pass "node_modules exists"
else
    warn "node_modules not found (run npm install)"
fi

if [ -f "next.config.js" ] || [ -f "next.config.mjs" ]; then
    pass "Next.js config exists"
else
    warn "Next.js config not found"
fi

echo ""

# ============================================================
# Summary
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}  Verification Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✓ Passed:${NC}   $PASSED"
echo -e "${YELLOW}⚠ Warnings:${NC} $WARNINGS"
echo -e "${RED}✗ Failed:${NC}   $FAILED"
echo ""

TOTAL_CHECKS=$((PASSED + WARNINGS + FAILED))

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  ✓ PRODUCTION READY${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "🎉 All checks passed! Application is ready for production deployment."
        echo ""
        echo "📋 Next Steps:"
        echo "   1. Review PRODUCTION_DEPLOYMENT_CHECKLIST.md"
        echo "   2. Prepare production server"
        echo "   3. Create .env.production with production values"
        echo "   4. Run deploy_production.sh on production server"
        echo "   5. Monitor deployment using PRODUCTION_RUNBOOK.md"
        echo ""
        exit 0
    else
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}  ⚠ PRODUCTION READY (WITH WARNINGS)${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "⚠ Application is mostly ready, but please review warnings above."
        echo ""
        echo "Recommendation: Address warnings before production deployment."
        echo ""
        exit 0
    fi
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  ✗ NOT READY FOR PRODUCTION${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "❌ $FAILED critical issues found. Please fix before deploying."
    echo ""
    echo "📋 Action Required:"
    echo "   1. Review failed checks above"
    echo "   2. Fix all critical issues"
    echo "   3. Run this script again"
    echo "   4. Only deploy when all checks pass"
    echo ""
    exit 1
fi
