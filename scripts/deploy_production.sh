#!/bin/bash
#
# AR Control Hub - Production Deployment Script
#
# This script automates the production deployment process.
# Run this on the production server after manual prerequisites are complete.
#
# Prerequisites:
#   - PostgreSQL installed and running
#   - Production database created
#   - .env.production file configured
#   - Repository cloned to /opt/ar-control-hub
#
# Usage:
#   sudo ./scripts/deploy_production.sh
#

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
APP_DIR="/opt/ar-control-hub"
APP_USER="arapp"
LOG_DIR="/var/log/ar-control-hub"
BACKUP_DIR="/var/backups/ar-control-hub"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}  AR Control Hub - Production Deployment${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Check if .env.production exists
if [ ! -f "$APP_DIR/.env.production" ]; then
    echo -e "${RED}Error: .env.production not found in $APP_DIR${NC}"
    echo "Please create .env.production with production configuration"
    exit 1
fi

echo -e "${YELLOW}[1/10] Checking Prerequisites${NC}"

# Check PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    echo -e "${RED}PostgreSQL is not running${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ PostgreSQL running${NC}"

# Check if app user exists
if ! id -u $APP_USER > /dev/null 2>&1; then
    echo -e "${YELLOW}  Creating application user: $APP_USER${NC}"
    useradd -m -s /bin/bash $APP_USER
fi
echo -e "${GREEN}  ✓ Application user exists${NC}"

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}Application directory $APP_DIR not found${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Application directory exists${NC}"

echo ""
echo -e "${YELLOW}[2/10] Creating Directories${NC}"

# Create log directory
mkdir -p $LOG_DIR
chown $APP_USER:$APP_USER $LOG_DIR
echo -e "${GREEN}  ✓ Log directory: $LOG_DIR${NC}"

# Create backup directory
mkdir -p $BACKUP_DIR
chown $APP_USER:$APP_USER $BACKUP_DIR
echo -e "${GREEN}  ✓ Backup directory: $BACKUP_DIR${NC}"

echo ""
echo -e "${YELLOW}[3/10] Installing System Dependencies${NC}"

apt update -qq
apt install -y python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx postgresql-client -qq
echo -e "${GREEN}  ✓ System dependencies installed${NC}"

echo ""
echo -e "${YELLOW}[4/10] Setting Up Python Environment${NC}"

cd $APP_DIR

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    sudo -u $APP_USER python3 -m venv venv
    echo -e "${GREEN}  ✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}  ✓ Virtual environment exists${NC}"
fi

# Install Python dependencies
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install --upgrade pip -q && pip install -r requirements.txt -q"
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install gunicorn uvicorn[standard] -q"
echo -e "${GREEN}  ✓ Python dependencies installed${NC}"

echo ""
echo -e "${YELLOW}[5/10] Running Database Migrations${NC}"

# Load environment variables
export $(grep -v '^#' .env.production | xargs)

# Run migrations as app user
sudo -u $APP_USER bash -c "source venv/bin/activate && export \$(grep -v '^#' .env.production | xargs) && alembic upgrade head"
echo -e "${GREEN}  ✓ Database migrations completed${NC}"

echo ""
echo -e "${YELLOW}[6/10] Building Frontend${NC}"

# Install Node dependencies
sudo -u $APP_USER npm install --production --quiet
echo -e "${GREEN}  ✓ Node dependencies installed${NC}"

# Build frontend
sudo -u $APP_USER npm run build
echo -e "${GREEN}  ✓ Frontend built${NC}"

echo ""
echo -e "${YELLOW}[7/10] Configuring Systemd Services${NC}"

# Backend service
cat > /etc/systemd/system/ar-backend.service <<EOF
[Unit]
Description=AR Control Hub Backend API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env.production
ExecStart=$APP_DIR/venv/bin/gunicorn src.api.main:app \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 0.0.0.0:8000 \\
    --timeout 60 \\
    --access-logfile $LOG_DIR/access.log \\
    --error-logfile $LOG_DIR/error.log \\
    --log-level info

Restart=always
RestartSec=10
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}  ✓ Backend service configured${NC}"

# Frontend service
cat > /etc/systemd/system/ar-frontend.service <<EOF
[Unit]
Description=AR Control Hub Frontend
After=network.target ar-backend.service
Requires=ar-backend.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="NODE_ENV=production"
EnvironmentFile=$APP_DIR/.env.production
ExecStart=/usr/bin/npm run start

Restart=always
RestartSec=10
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}  ✓ Frontend service configured${NC}"

# Reload systemd
systemctl daemon-reload

echo ""
echo -e "${YELLOW}[8/10] Starting Services${NC}"

# Start and enable backend
systemctl start ar-backend
systemctl enable ar-backend
echo -e "${GREEN}  ✓ Backend started${NC}"

# Wait for backend to be ready
sleep 5

# Check backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}  ✓ Backend health check passed${NC}"
else
    echo -e "${RED}  ✗ Backend health check failed${NC}"
    echo "  Check logs: journalctl -u ar-backend -n 50"
    exit 1
fi

# Start and enable frontend
systemctl start ar-frontend
systemctl enable ar-frontend
echo -e "${GREEN}  ✓ Frontend started${NC}"

# Wait for frontend
sleep 5

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}  ✓ Frontend health check passed${NC}"
else
    echo -e "${YELLOW}  ⚠ Frontend may still be starting...${NC}"
fi

echo ""
echo -e "${YELLOW}[9/10] Configuring Log Rotation${NC}"

cat > /etc/logrotate.d/ar-control-hub <<EOF
$LOG_DIR/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 $APP_USER $APP_USER
    sharedscripts
    postrotate
        systemctl reload ar-backend > /dev/null 2>&1 || true
    endscript
}
EOF

echo -e "${GREEN}  ✓ Log rotation configured${NC}"

echo ""
echo -e "${YELLOW}[10/10] Setting Up Automated Backups${NC}"

# Make backup script executable
chmod +x $APP_DIR/scripts/backup_database.sh
chmod +x $APP_DIR/scripts/health_check.sh

# Add cron jobs for app user
(crontab -u $APP_USER -l 2>/dev/null; echo "# AR Control Hub - Daily database backup at 2:00 AM") | crontab -u $APP_USER -
(crontab -u $APP_USER -l 2>/dev/null; echo "0 2 * * * $APP_DIR/scripts/backup_database.sh") | crontab -u $APP_USER -
(crontab -u $APP_USER -l 2>/dev/null; echo "# AR Control Hub - Health check every 5 minutes") | crontab -u $APP_USER -
(crontab -u $APP_USER -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/scripts/health_check.sh >> $LOG_DIR/health_check.log 2>&1") | crontab -u $APP_USER -

echo -e "${GREEN}  ✓ Automated backups configured${NC}"
echo -e "${GREEN}  ✓ Health checks configured${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}  ✅ Deployment Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Service Status:"
echo "   Backend:  $(systemctl is-active ar-backend)"
echo "   Frontend: $(systemctl is-active ar-frontend)"
echo ""
echo "🔗 Application URLs:"
echo "   Backend API: http://localhost:8000"
echo "   Frontend:    http://localhost:3000"
echo "   Health:      http://localhost:8000/health"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "📝 Next Steps:"
echo "   1. Configure Nginx reverse proxy (see PRODUCTION_DEPLOYMENT_CHECKLIST.md)"
echo "   2. Obtain SSL certificate: sudo certbot --nginx -d ar.company.com"
echo "   3. Create admin user: sudo -u $APP_USER bash -c 'source venv/bin/activate && python scripts/create_admin_user.py --email admin@company.com --username admin --password \"SecurePass123!\" --full-name \"Admin\"'"
echo "   4. Test application: curl http://localhost:8000/health"
echo "   5. Review logs: tail -f $LOG_DIR/*.log"
echo ""
echo "📊 Monitoring:"
echo "   View backend logs:  journalctl -u ar-backend -f"
echo "   View frontend logs: journalctl -u ar-frontend -f"
echo "   Check service status: systemctl status ar-backend ar-frontend"
echo ""
echo "🔐 Security Reminders:"
echo "   - Configure firewall (UFW): see PRODUCTION_DEPLOYMENT_CHECKLIST.md"
echo "   - Set up Fail2Ban for SSH protection"
echo "   - Review .env.production for sensitive data"
echo "   - Ensure strong passwords for all accounts"
echo ""
echo -e "${BLUE}Happy deploying! 🚀${NC}"
echo ""
