#!/bin/bash
#
# AR Control Hub - Demo Environment Setup Script
#
# This script prepares a clean demo environment with sample data.
# Run this 1 day before the demo to ensure everything is ready.
#
# Usage:
#   ./scripts/setup_demo_environment.sh
#

set -e  # Exit on error

echo "🚀 Setting up AR Control Hub Demo Environment..."
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "scripts/seed_demo_data.py" ]; then
    echo -e "${RED}Error: Please run this script from the AR1 project root directory${NC}"
    exit 1
fi

# Step 1: Create demo database
echo -e "${YELLOW}[1/7] Setting up demo database...${NC}"
export DATABASE_URL="postgresql+asyncpg://ar_user:ar_dev_password@localhost:5432/ar_demo"

# Check if database exists, create if not
psql -U postgres -lqt | cut -d \| -f 1 | grep -qw ar_demo || {
    echo "  Creating ar_demo database..."
    psql -U postgres -c "CREATE DATABASE ar_demo;"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ar_demo TO ar_user;"
}
echo -e "${GREEN}  ✓ Database ready${NC}"

# Step 2: Run migrations
echo -e "${YELLOW}[2/7] Running database migrations...${NC}"
alembic upgrade head
echo -e "${GREEN}  ✓ Migrations complete${NC}"

# Step 3: Install Python dependencies (including Faker)
echo -e "${YELLOW}[3/7] Checking Python dependencies...${NC}"
pip install faker --quiet
echo -e "${GREEN}  ✓ Dependencies installed${NC}"

# Step 4: Generate demo data
echo -e "${YELLOW}[4/7] Generating realistic demo data...${NC}"
python scripts/seed_demo_data.py --scenario demo
echo -e "${GREEN}  ✓ Demo data created${NC}"

# Step 5: Create demo user accounts
echo -e "${YELLOW}[5/7] Creating demo user accounts...${NC}"
echo "  Users created:"
echo "    - sarah.martinez@company.com (AR Specialist) - Password: demo123"
echo "    - michael.chen@company.com (AR Manager) - Password: demo123"
echo "    - admin@company.com (Admin) - Password: demo123"
echo -e "${GREEN}  ✓ User accounts ready${NC}"

# Step 6: Start backend server (in background)
echo -e "${YELLOW}[6/7] Starting backend server...${NC}"
pkill -f "uvicorn src.api.main:app" 2>/dev/null || true  # Kill existing
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs/demo_backend.log 2>&1 &
sleep 3  # Wait for server to start

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}  ✓ Backend server running on http://localhost:8000${NC}"
else
    echo -e "${RED}  ✗ Backend server failed to start. Check logs/demo_backend.log${NC}"
    exit 1
fi

# Step 7: Start frontend server (in background)
echo -e "${YELLOW}[7/7] Starting frontend server...${NC}"
pkill -f "npm.*dev" 2>/dev/null || true  # Kill existing
nohup npm run dev > logs/demo_frontend.log 2>&1 &
sleep 5  # Wait for frontend to start

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}  ✓ Frontend server running on http://localhost:3000${NC}"
else
    echo -e "${RED}  ✗ Frontend server failed to start. Check logs/demo_frontend.log${NC}"
fi

echo ""
echo -e "${GREEN}✅ Demo environment setup complete!${NC}"
echo ""
echo "📋 Demo Environment Summary:"
echo "  • Database: ar_demo (50 customers, 200 invoices, $1M+ AR)"
echo "  • Backend API: http://localhost:8000"
echo "  • Frontend: http://localhost:3000"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
echo "👤 Demo User Accounts:"
echo "  • sarah.martinez@company.com / demo123 (AR Specialist)"
echo "  • michael.chen@company.com / demo123 (AR Manager)"
echo "  • admin@company.com / demo123 (Admin)"
echo ""
echo "🎯 Next Steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Login with any demo account above"
echo "  3. Review the demo script in DEMO_GUIDE.md"
echo "  4. Practice your presentation!"
echo ""
echo "🛑 To stop servers:"
echo "  pkill -f 'uvicorn src.api.main:app'"
echo "  pkill -f 'npm.*dev'"
echo ""
echo "📊 To view server logs:"
echo "  tail -f logs/demo_backend.log"
echo "  tail -f logs/demo_frontend.log"
echo ""
echo -e "${YELLOW}Happy demoing! 🚀${NC}"
