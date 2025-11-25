# AR Control Hub - Production Deployment Checklist

**Deployment Date:** ________________
**Deployed By:** ________________
**Deployment Type:** ☐ Initial Deployment  ☐ Update  ☐ Rollback

---

## Pre-Deployment Requirements

### Infrastructure Requirements
- [ ] Production server provisioned (min 4 CPU, 8GB RAM, 100GB SSD)
- [ ] PostgreSQL 14+ installed
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ and npm installed
- [ ] Nginx installed
- [ ] SSL certificate obtained (Let's Encrypt or commercial)
- [ ] Domain name configured (e.g., ar.company.com)
- [ ] Firewall rules configured (ports 80, 443, 5432)
- [ ] Backup storage configured

### Access & Permissions
- [ ] SSH access to production server
- [ ] sudo/root access for system configuration
- [ ] Database admin credentials
- [ ] SSL certificate files
- [ ] Git repository access from production server

### Pre-Deployment Testing
- [ ] All unit tests passing (`pytest`)
- [ ] Integration tests passing
- [ ] Security scan completed (no critical vulnerabilities)
- [ ] Performance testing completed
- [ ] UAT completed with sign-off
- [ ] Backup and restore procedures tested

---

## Phase 1: Database Setup

### 1.1 PostgreSQL Installation & Configuration

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-14 postgresql-contrib-14

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

- [ ] PostgreSQL installed
- [ ] PostgreSQL service running

### 1.2 Create Production Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE ar_control_hub_prod;
CREATE USER ar_admin WITH ENCRYPTED PASSWORD 'SECURE_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE ar_control_hub_prod TO ar_admin;

# Grant schema permissions
\c ar_control_hub_prod
GRANT ALL ON SCHEMA public TO ar_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ar_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ar_admin;

\q
```

- [ ] Database `ar_control_hub_prod` created
- [ ] User `ar_admin` created with strong password
- [ ] Permissions granted

### 1.3 Configure PostgreSQL for Production

Edit `/etc/postgresql/14/main/postgresql.conf`:

```ini
# Performance Tuning
shared_buffers = 2GB                    # 25% of RAM
effective_cache_size = 6GB              # 75% of RAM
maintenance_work_mem = 512MB
work_mem = 16MB
max_connections = 100

# Write-Ahead Logging
wal_level = replica
max_wal_size = 2GB
min_wal_size = 1GB

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_rotation_age = 1d
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_min_duration_statement = 1000      # Log slow queries (>1s)
```

Edit `/etc/postgresql/14/main/pg_hba.conf`:

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     peer
host    ar_control_hub_prod  ar_admin   127.0.0.1/32           scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256
```

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql
```

- [ ] PostgreSQL performance tuned
- [ ] Logging configured
- [ ] Authentication configured
- [ ] PostgreSQL restarted

### 1.4 Test Database Connection

```bash
# Test connection
PGPASSWORD='SECURE_PASSWORD_HERE' psql -U ar_admin -d ar_control_hub_prod -h localhost -c "SELECT version();"
```

- [ ] Database connection successful

---

## Phase 2: Application Deployment

### 2.1 Create Production User & Directory

```bash
# Create application user
sudo useradd -m -s /bin/bash arapp
sudo usermod -aG sudo arapp  # Optional: if app needs sudo

# Create application directory
sudo mkdir -p /opt/ar-control-hub
sudo chown arapp:arapp /opt/ar-control-hub

# Switch to app user
sudo su - arapp
cd /opt/ar-control-hub
```

- [ ] Application user created
- [ ] Application directory created

### 2.2 Clone Repository

```bash
# Clone from Git
git clone https://github.com/your-org/AR1.git .

# Or use your specific branch
git clone -b claude/ar-management-system-01Gf8fvBypEDP3cacv7SzAML https://github.com/your-org/AR1.git .

# Checkout specific tag/release
git checkout v1.0.0  # Use tagged release for production
```

- [ ] Repository cloned
- [ ] Correct branch/tag checked out

### 2.3 Python Backend Setup

```bash
# Install Python dependencies
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Install production-only packages
pip install gunicorn uvicorn[standard]
```

- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Production server (gunicorn/uvicorn) installed

### 2.4 Configure Production Environment Variables

Create `/opt/ar-control-hub/.env.production`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://ar_admin:SECURE_PASSWORD_HERE@localhost:5432/ar_control_hub_prod

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production

# Security
JWT_SECRET_KEY=GENERATE_STRONG_RANDOM_KEY_HERE_64_CHARS_MIN
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS (adjust to your frontend domain)
CORS_ORIGINS=https://ar.company.com,https://www.company.com

# Email (configure your SMTP server)
SMTP_HOST=smtp.company.com
SMTP_PORT=587
SMTP_USERNAME=ar-notifications@company.com
SMTP_PASSWORD=EMAIL_PASSWORD_HERE
SMTP_FROM_EMAIL=ar-notifications@company.com
SMTP_FROM_NAME=AR Control Hub

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ar-control-hub/app.log

# Epicor Integration
EPICOR_API_URL=https://epicor.company.com/api
EPICOR_API_KEY=EPICOR_API_KEY_HERE
EPICOR_COMPANY_ID=COMPANY_ID

# Feature Flags
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_DAILY_DIGEST=true
ENABLE_EPICOR_IMPORT=true
```

**Generate JWT Secret:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

- [ ] `.env.production` created
- [ ] All secrets configured
- [ ] JWT secret generated (64+ characters)
- [ ] CORS origins set to production domains
- [ ] Email SMTP configured

### 2.5 Run Database Migrations

```bash
# Set environment to production
export $(cat .env.production | xargs)

# Run Alembic migrations
alembic upgrade head

# Verify migrations
PGPASSWORD='SECURE_PASSWORD_HERE' psql -U ar_admin -d ar_control_hub_prod -c "\dt"
```

- [ ] Migrations executed successfully
- [ ] All tables created
- [ ] Schema verified

### 2.6 Create Production Admin User

```bash
# Create admin user script
python3 scripts/create_admin_user.py \
  --email admin@company.com \
  --username admin \
  --password 'ADMIN_PASSWORD_HERE' \
  --full-name "System Administrator"
```

- [ ] Admin user created
- [ ] Admin credentials documented securely

### 2.7 Frontend Build & Deployment

```bash
# Install Node dependencies
npm install --production

# Create production build
npm run build

# Verify build
ls -la .next/
```

- [ ] Node dependencies installed
- [ ] Production build successful
- [ ] Build artifacts verified

---

## Phase 3: Web Server Configuration (Nginx)

### 3.1 Install Nginx

```bash
sudo apt update
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

- [ ] Nginx installed
- [ ] Nginx service running

### 3.2 Configure Nginx for AR Control Hub

Create `/etc/nginx/sites-available/ar-control-hub`:

```nginx
# Backend API (port 8000)
upstream backend_api {
    server 127.0.0.1:8000;
    keepalive 64;
}

# Frontend (port 3000)
upstream frontend_app {
    server 127.0.0.1:3000;
    keepalive 64;
}

# HTTP -> HTTPS Redirect
server {
    listen 80;
    listen [::]:80;
    server_name ar.company.com;

    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ar.company.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/ar.company.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ar.company.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/ar-control-hub-access.log;
    error_log /var/log/nginx/ar-control-hub-error.log;

    # API Backend (proxy to port 8000)
    location /api/ {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health Check
    location /health {
        proxy_pass http://backend_api/health;
        access_log off;
    }

    # API Documentation
    location /docs {
        proxy_pass http://backend_api/docs;
        proxy_set_header Host $host;
    }

    # Frontend (proxy to port 3000)
    location / {
        proxy_pass http://frontend_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (Next.js)
    location /_next/static/ {
        proxy_pass http://frontend_app;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, immutable";
    }

    # Favicon, robots.txt
    location ~* \.(ico|txt)$ {
        proxy_pass http://frontend_app;
        access_log off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ar-control-hub /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

- [ ] Nginx configuration created
- [ ] Site enabled
- [ ] Configuration tested (nginx -t)
- [ ] Nginx reloaded

### 3.3 SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d ar.company.com

# Test auto-renewal
sudo certbot renew --dry-run
```

- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] Auto-renewal configured
- [ ] Certificate verified

---

## Phase 4: Process Management (systemd)

### 4.1 Backend API Service

Create `/etc/systemd/system/ar-backend.service`:

```ini
[Unit]
Description=AR Control Hub Backend API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=arapp
Group=arapp
WorkingDirectory=/opt/ar-control-hub
Environment="PATH=/opt/ar-control-hub/venv/bin"
EnvironmentFile=/opt/ar-control-hub/.env.production
ExecStart=/opt/ar-control-hub/venv/bin/gunicorn src.api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 60 \
    --access-logfile /var/log/ar-control-hub/access.log \
    --error-logfile /var/log/ar-control-hub/error.log \
    --log-level info

# Restart policy
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/ar-control-hub
sudo chown arapp:arapp /var/log/ar-control-hub

# Reload systemd
sudo systemctl daemon-reload

# Start backend
sudo systemctl start ar-backend

# Enable on boot
sudo systemctl enable ar-backend

# Check status
sudo systemctl status ar-backend
```

- [ ] Backend service file created
- [ ] Log directory created
- [ ] Service started successfully
- [ ] Service enabled on boot
- [ ] Backend responding on port 8000

### 4.2 Frontend Service

Create `/etc/systemd/system/ar-frontend.service`:

```ini
[Unit]
Description=AR Control Hub Frontend
After=network.target ar-backend.service
Requires=ar-backend.service

[Service]
Type=simple
User=arapp
Group=arapp
WorkingDirectory=/opt/ar-control-hub
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="NODE_ENV=production"
EnvironmentFile=/opt/ar-control-hub/.env.production
ExecStart=/usr/bin/npm run start

# Restart policy
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start frontend
sudo systemctl start ar-frontend

# Enable on boot
sudo systemctl enable ar-frontend

# Check status
sudo systemctl status ar-frontend
```

- [ ] Frontend service file created
- [ ] Service started successfully
- [ ] Service enabled on boot
- [ ] Frontend responding on port 3000

---

## Phase 5: Monitoring & Logging

### 5.1 Log Rotation

Create `/etc/logrotate.d/ar-control-hub`:

```
/var/log/ar-control-hub/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 arapp arapp
    sharedscripts
    postrotate
        systemctl reload ar-backend > /dev/null 2>&1 || true
    endscript
}
```

- [ ] Log rotation configured

### 5.2 Application Monitoring

Create `/opt/ar-control-hub/scripts/health_check.sh`:

```bash
#!/bin/bash
# Health check script for monitoring

# Check backend health
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$BACKEND_STATUS" != "200" ]; then
    echo "CRITICAL: Backend API not responding (HTTP $BACKEND_STATUS)"
    exit 2
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" != "200" ]; then
    echo "WARNING: Frontend not responding (HTTP $FRONTEND_STATUS)"
    exit 1
fi

# Check database connection
PGPASSWORD='SECURE_PASSWORD_HERE' psql -U ar_admin -d ar_control_hub_prod -c "SELECT 1;" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "CRITICAL: Database connection failed"
    exit 2
fi

echo "OK: All services healthy"
exit 0
```

```bash
chmod +x /opt/ar-control-hub/scripts/health_check.sh
```

- [ ] Health check script created
- [ ] Script executable

### 5.3 Monitoring with Cron

```bash
# Add to crontab for user arapp
crontab -e

# Add this line (check every 5 minutes)
*/5 * * * * /opt/ar-control-hub/scripts/health_check.sh >> /var/log/ar-control-hub/health_check.log 2>&1
```

- [ ] Cron job configured for health checks

---

## Phase 6: Backup & Disaster Recovery

### 6.1 Database Backup Script

Create `/opt/ar-control-hub/scripts/backup_database.sh`:

```bash
#!/bin/bash
# Database backup script

BACKUP_DIR="/var/backups/ar-control-hub"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ar_prod_backup_$TIMESTAMP.sql"
DB_NAME="ar_control_hub_prod"
DB_USER="ar_admin"
DB_PASSWORD="SECURE_PASSWORD_HERE"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Perform backup
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_FILE.gz

# Check if backup successful
if [ $? -eq 0 ]; then
    echo "$(date): Backup successful: $BACKUP_FILE.gz" >> /var/log/ar-control-hub/backup.log

    # Delete backups older than 30 days
    find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
else
    echo "$(date): Backup FAILED" >> /var/log/ar-control-hub/backup.log
    exit 1
fi
```

```bash
chmod +x /opt/ar-control-hub/scripts/backup_database.sh
sudo mkdir -p /var/backups/ar-control-hub
sudo chown arapp:arapp /var/backups/ar-control-hub
```

- [ ] Backup script created
- [ ] Backup directory created
- [ ] Script executable

### 6.2 Automated Daily Backups

```bash
# Add to crontab for user arapp
crontab -e

# Daily backup at 2:00 AM
0 2 * * * /opt/ar-control-hub/scripts/backup_database.sh
```

- [ ] Daily backup cron job configured

### 6.3 Test Backup Restore

```bash
# Create test database
PGPASSWORD='SECURE_PASSWORD_HERE' psql -U ar_admin -h localhost -c "CREATE DATABASE ar_test_restore;"

# Restore latest backup
LATEST_BACKUP=$(ls -t /var/backups/ar-control-hub/*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | PGPASSWORD='SECURE_PASSWORD_HERE' psql -U ar_admin -h localhost ar_test_restore

# Verify restore
PGPASSWORD='SECURE_PASSWORD_HERE' psql -U ar_admin -h localhost ar_test_restore -c "SELECT COUNT(*) FROM customers;"

# Cleanup test database
PGPASSWORD='SECURE_PASSWORD_HERE' psql -U ar_admin -h localhost -c "DROP DATABASE ar_test_restore;"
```

- [ ] Backup restore tested successfully

---

## Phase 7: Security Hardening

### 7.1 Firewall Configuration (UFW)

```bash
# Install UFW
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow PostgreSQL only from localhost (already default, but explicit)
sudo ufw deny 5432/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

- [ ] Firewall configured
- [ ] Only necessary ports open (22, 80, 443)
- [ ] Database port (5432) not exposed

### 7.2 Fail2Ban (Brute Force Protection)

```bash
# Install Fail2Ban
sudo apt install fail2ban

# Create local config
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Edit /etc/fail2ban/jail.local
# Enable SSH protection
[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600

# Start Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

- [ ] Fail2Ban installed
- [ ] SSH protection enabled
- [ ] Fail2Ban running

### 7.3 Application Security Checklist

- [ ] All secrets in `.env.production` (not in code)
- [ ] Strong passwords used (16+ characters)
- [ ] JWT secret is cryptographically random (64+ chars)
- [ ] CORS configured to only allow production domains
- [ ] SQL injection protection (using ORM parameterized queries)
- [ ] XSS protection (Next.js auto-escaping)
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Security headers configured in Nginx

---

## Phase 8: Production Validation

### 8.1 Smoke Tests

```bash
# Test backend health
curl https://ar.company.com/health

# Test API endpoint
curl https://ar.company.com/api/v1/dashboard/summary

# Test frontend loads
curl -I https://ar.company.com

# Test HTTPS redirect
curl -I http://ar.company.com
```

- [ ] Backend health check returns 200
- [ ] API endpoints responding
- [ ] Frontend loads successfully
- [ ] HTTP redirects to HTTPS

### 8.2 Login Test

- [ ] Open https://ar.company.com in browser
- [ ] Login with admin user created earlier
- [ ] Dashboard loads with no errors
- [ ] Navigate to all major pages (worklist, customers, analytics)
- [ ] No console errors in browser DevTools

### 8.3 Database Validation

```bash
# Check record counts
PGPASSWORD='SECURE_PASSWORD_HERE' psql -U ar_admin -d ar_control_hub_prod -c "
SELECT
    'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'invoices', COUNT(*) FROM invoices
UNION ALL
SELECT 'payments', COUNT(*) FROM payments;
"
```

- [ ] Users table has admin user
- [ ] Database schema correct
- [ ] No errors in database logs

### 8.4 Performance Test

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test backend API (100 requests, 10 concurrent)
ab -n 100 -c 10 https://ar.company.com/api/v1/dashboard/summary

# Test frontend
ab -n 100 -c 10 https://ar.company.com/
```

- [ ] API response time < 500ms (p95)
- [ ] No failed requests
- [ ] Frontend loads < 2 seconds

---

## Phase 9: Documentation & Handoff

### 9.1 Production Runbook

- [ ] Document server details (IP, hostname, credentials)
- [ ] Document all service commands (start, stop, restart, status)
- [ ] Document backup location and restore procedure
- [ ] Document log file locations
- [ ] Document monitoring and alerting setup
- [ ] Create troubleshooting guide

### 9.2 Access Documentation

Create `/opt/ar-control-hub/PRODUCTION_ACCESS.md`:

```markdown
# Production Access Guide

## Server Access
- **Hostname:** ar.company.com
- **IP Address:** [IP_ADDRESS]
- **SSH:** ssh arapp@ar.company.com
- **SSH Key:** [Location of SSH key]

## Application URLs
- **Frontend:** https://ar.company.com
- **API Docs:** https://ar.company.com/docs
- **Health Check:** https://ar.company.com/health

## Database Access
- **Host:** localhost (from server only)
- **Database:** ar_control_hub_prod
- **User:** ar_admin
- **Password:** [Stored in 1Password/KeePass]

## Service Management
```bash
# Backend
sudo systemctl status ar-backend
sudo systemctl restart ar-backend
sudo systemctl stop ar-backend
sudo systemctl start ar-backend

# Frontend
sudo systemctl status ar-frontend
sudo systemctl restart ar-frontend

# Nginx
sudo systemctl status nginx
sudo systemctl reload nginx

# PostgreSQL
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

## Log Locations
- **Application Logs:** /var/log/ar-control-hub/
- **Nginx Logs:** /var/log/nginx/
- **PostgreSQL Logs:** /var/log/postgresql/

## Backups
- **Location:** /var/backups/ar-control-hub/
- **Schedule:** Daily at 2:00 AM
- **Retention:** 30 days

## Emergency Contacts
- **System Admin:** [Name] - [Phone] - [Email]
- **Database Admin:** [Name] - [Phone] - [Email]
- **Application Owner:** [Name] - [Phone] - [Email]
```

- [ ] Production access documented
- [ ] Credentials stored securely
- [ ] Emergency contacts documented

### 9.3 Deployment Notes

Document in this checklist:
- **Deployment Date:** ________________
- **Deployment Time:** ________________
- **Git Commit/Tag:** ________________
- **Database Migration Version:** ________________
- **Any Issues Encountered:** ________________
- **Resolution:** ________________

---

## Post-Deployment Monitoring

### First 24 Hours
- [ ] Monitor error logs every hour
- [ ] Check health check logs
- [ ] Monitor database performance
- [ ] Monitor server resources (CPU, RAM, disk)
- [ ] Be available for user support

### First Week
- [ ] Daily log review
- [ ] Monitor backup success
- [ ] Track user feedback
- [ ] Monitor performance metrics
- [ ] Document any issues and resolutions

### First Month
- [ ] Weekly performance review
- [ ] Review and tune database queries
- [ ] Optimize slow endpoints
- [ ] Update documentation based on learnings
- [ ] Plan for Phase 4 features (if applicable)

---

## Rollback Procedure (Emergency)

### If Critical Issue Found:

1. **Restore Database Backup:**
```bash
# Stop backend
sudo systemctl stop ar-backend

# Restore latest backup
LATEST_BACKUP=$(ls -t /var/backups/ar-control-hub/*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | PGPASSWORD='SECURE_PASSWORD_HERE' psql -U ar_admin -h localhost ar_control_hub_prod

# Start backend
sudo systemctl start ar-backend
```

2. **Revert Code:**
```bash
cd /opt/ar-control-hub
git checkout [PREVIOUS_STABLE_TAG]
alembic downgrade [PREVIOUS_MIGRATION]

# Rebuild frontend
npm run build

# Restart services
sudo systemctl restart ar-backend
sudo systemctl restart ar-frontend
```

3. **Verify Rollback:**
- [ ] Application accessible
- [ ] Users can login
- [ ] Critical functions working
- [ ] Communicate status to users

---

## Deployment Sign-Off

**Pre-Deployment Approval:**
- [ ] Project Lead: ________________ (Signature/Date)
- [ ] IT Manager: ________________ (Signature/Date)
- [ ] Security Officer: ________________ (Signature/Date)

**Post-Deployment Verification:**
- [ ] All smoke tests passed
- [ ] Production validation complete
- [ ] Monitoring configured
- [ ] Backups verified
- [ ] Documentation complete

**Go-Live Approval:**
- [ ] Project Lead: ________________ (Signature/Date)
- [ ] Business Owner: ________________ (Signature/Date)

---

## Success Criteria

**Deployment is considered successful when:**
- ✅ Application accessible via HTTPS
- ✅ All services running and healthy
- ✅ Admin can login successfully
- ✅ Dashboard loads with correct data
- ✅ No errors in logs
- ✅ Backups configured and tested
- ✅ Monitoring and alerting active
- ✅ Performance meets SLA (API < 500ms, Frontend < 2s)
- ✅ Security scan shows no critical vulnerabilities
- ✅ Documentation complete

---

**Congratulations on deploying AR Control Hub to production! 🚀**
