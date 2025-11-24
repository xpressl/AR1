# AR Control Hub - Deployment Guide

## Pre-Deployment Checklist

### 1. Environment Preparation

#### Production Server Requirements
- **CPU:** 4+ cores recommended
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 50GB minimum for database and logs
- **OS:** Ubuntu 20.04+ or similar Linux distribution
- **Network:** HTTPS (port 443), SSH (port 22)

#### Software Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install PostgreSQL 14
sudo apt install postgresql-14 postgresql-contrib -y

# Install Nginx (reverse proxy)
sudo apt install nginx -y

# Install certbot (SSL certificates)
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Database Setup

#### Create Production Database
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE ar_control_hub_prod;
CREATE USER ar_admin WITH ENCRYPTED PASSWORD 'your-secure-password-here';
GRANT ALL PRIVILEGES ON DATABASE ar_control_hub_prod TO ar_admin;

# Enable required extensions
\c ar_control_hub_prod
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\q
```

#### Configure PostgreSQL for Production
Edit `/etc/postgresql/14/main/postgresql.conf`:
```
# Memory settings (adjust based on available RAM)
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 32MB

# Connection settings
max_connections = 100

# Performance
random_page_cost = 1.1
effective_io_concurrency = 200
```

Edit `/etc/postgresql/14/main/pg_hba.conf`:
```
# Allow local connections
host    ar_control_hub_prod    ar_admin    127.0.0.1/32    md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 3. Application Deployment

#### Create Application User
```bash
sudo useradd -m -s /bin/bash ar-app
sudo su - ar-app
```

#### Clone and Setup Application
```bash
# Clone repository
git clone <repository-url> /home/ar-app/ar-control-hub
cd /home/ar-app/ar-control-hub

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Node dependencies
npm ci --production
```

#### Configure Environment Variables
Create `/home/ar-app/ar-control-hub/.env`:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://ar_admin:your-secure-password-here@localhost:5432/ar_control_hub_prod

# API
API_PORT=8000
CORS_ORIGINS=https://ar.yourcompany.com
ENVIRONMENT=production
LOG_LEVEL=WARNING

# Authentication
JWT_SECRET_KEY=generate-a-secure-random-key-minimum-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=ar-notifications@yourcompany.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@yourcompany.com
SMTP_FROM_NAME=AR Control Hub

# Data Import
EPICOR_EXPORT_PATH=/mnt/epicor-exports
ENABLE_SCHEDULER=true
IMPORT_SCHEDULE_CRON=0 6 * * *

# Notifications
DAILY_DIGEST_SCHEDULE=30 6 * * *
DIGEST_RECIPIENTS=ar-team@yourcompany.com,finance@yourcompany.com

# Security
ALLOWED_HOSTS=ar.yourcompany.com
SECURE_COOKIES=true
```

**Generate Secure JWT Secret:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Run Database Migrations
```bash
source venv/bin/activate
alembic upgrade head
```

#### Build Frontend
```bash
npm run build
```

### 4. Create Systemd Services

#### Backend API Service
Create `/etc/systemd/system/ar-api.service`:
```ini
[Unit]
Description=AR Control Hub API
After=network.target postgresql.service

[Service]
Type=notify
User=ar-app
Group=ar-app
WorkingDirectory=/home/ar-app/ar-control-hub
Environment="PATH=/home/ar-app/ar-control-hub/venv/bin"
ExecStart=/home/ar-app/ar-control-hub/venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Frontend Service (if using npm)
Create `/etc/systemd/system/ar-frontend.service`:
```ini
[Unit]
Description=AR Control Hub Frontend
After=network.target

[Service]
Type=simple
User=ar-app
Group=ar-app
WorkingDirectory=/home/ar-app/ar-control-hub
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable ar-api ar-frontend
sudo systemctl start ar-api ar-frontend

# Check status
sudo systemctl status ar-api
sudo systemctl status ar-frontend
```

### 5. Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/ar-control-hub`:
```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

upstream api_backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name ar.yourcompany.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ar.yourcompany.com;

    # SSL certificates (will be configured by certbot)
    ssl_certificate /etc/letsencrypt/live/ar.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ar.yourcompany.com/privkey.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API proxy
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check (no rate limit)
    location /health {
        proxy_pass http://api_backend;
        access_log off;
    }

    # API docs
    location ~ ^/(docs|redoc|openapi.json) {
        proxy_pass http://api_backend;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for Next.js HMR in dev)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site and obtain SSL certificate:
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ar-control-hub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Obtain SSL certificate
sudo certbot --nginx -d ar.yourcompany.com
```

### 6. Configure Firewall

```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 7. Setup Monitoring and Logs

#### Configure Log Rotation
Create `/etc/logrotate.d/ar-control-hub`:
```
/home/ar-app/ar-control-hub/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 ar-app ar-app
    sharedscripts
    postrotate
        systemctl reload ar-api > /dev/null 2>&1 || true
    endscript
}
```

#### Setup Health Check Monitoring
Create `/home/ar-app/health-check.sh`:
```bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $response -ne 200 ]; then
    echo "Health check failed with status $response"
    systemctl restart ar-api
    # Send alert email
    echo "AR Control Hub API health check failed" | mail -s "ALERT: AR API Down" admin@yourcompany.com
fi
```

Add to crontab:
```bash
sudo crontab -e
# Add line:
*/5 * * * * /home/ar-app/health-check.sh
```

### 8. Epicor Data Integration

#### Setup Shared Network Drive
```bash
# Create mount point
sudo mkdir -p /mnt/epicor-exports

# Mount Windows share (if Epicor exports to Windows network drive)
sudo apt install cifs-utils -y

# Add to /etc/fstab
//epicor-server/exports /mnt/epicor-exports cifs credentials=/home/ar-app/.epicor-creds,uid=ar-app,gid=ar-app 0 0

# Create credentials file
sudo nano /home/ar-app/.epicor-creds
# Add:
username=epicor_export_user
password=secure-password
domain=YOURDOMAIN

sudo chmod 600 /home/ar-app/.epicor-creds
sudo mount -a
```

#### Configure Epicor Export
In Epicor Eagle, setup scheduled export (Crystal Reports or SSRS):
- **Frequency:** Daily at 5:00 AM
- **Format:** CSV
- **Location:** `\\epicor-server\exports\`
- **Files to export:**
  - `customers.csv`
  - `invoices.csv`
  - `payments.csv`
  - `aging.csv`

### 9. Initial Data Load

```bash
# Activate virtual environment
source /home/ar-app/ar-control-hub/venv/bin/activate

# Trigger initial import
curl -X POST http://localhost:8000/api/imports/trigger -H "Authorization: Bearer <admin-token>"

# Monitor import logs
tail -f /home/ar-app/ar-control-hub/logs/import.log
```

### 10. Create Admin User

```bash
# Using Python shell
source venv/bin/activate
python3 << EOF
import asyncio
from src.db.connection import get_db
from src.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    async for db in get_db():
        admin = User(
            email="admin@yourcompany.com",
            full_name="AR Administrator",
            role="ar_manager",
            hashed_password=pwd_context.hash("change-this-password"),
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print(f"Admin user created: {admin.email}")
        break

asyncio.run(create_admin())
EOF
```

## Post-Deployment Verification

### 1. Health Checks
```bash
# API health check
curl https://ar.yourcompany.com/health

# Database connectivity
curl https://ar.yourcompany.com/api/dashboard/summary -H "Authorization: Bearer <token>"
```

### 2. Test Core Features
- [ ] Login with admin user
- [ ] View dashboard (should show real data after import)
- [ ] View customer list
- [ ] Create a test note
- [ ] Trigger manual import
- [ ] Check email notifications work
- [ ] View analytics dashboards (DSO, Cash Forecast)
- [ ] Test salesperson portal access

### 3. Performance Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils -y

# Load test (adjust concurrency and requests)
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" https://ar.yourcompany.com/api/dashboard/summary
```

### 4. Monitor Logs
```bash
# API logs
sudo journalctl -u ar-api -f

# Frontend logs
sudo journalctl -u ar-frontend -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

## Backup Strategy

### Database Backups
Create `/home/ar-app/backup-db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/home/ar-app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Dump database
pg_dump -U ar_admin -h localhost ar_control_hub_prod | gzip > $BACKUP_DIR/ar_db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "ar_db_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR/ar_db_$DATE.sql.gz s3://your-backup-bucket/ar-control-hub/
```

Add to crontab (daily at 2 AM):
```bash
0 2 * * * /home/ar-app/backup-db.sh
```

## Troubleshooting

### API Not Starting
```bash
# Check logs
sudo journalctl -u ar-api -n 100

# Test manually
source venv/bin/activate
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

### Database Connection Issues
```bash
# Test connection
psql -U ar_admin -h localhost -d ar_control_hub_prod

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Import Not Running
```bash
# Check scheduler status
curl http://localhost:8000/api/imports -H "Authorization: Bearer <token>"

# Manually trigger
curl -X POST http://localhost:8000/api/imports/trigger -H "Authorization: Bearer <token>"

# Check import logs
tail -f logs/import.log
```

### Email Not Sending
```bash
# Test SMTP connection
python3 << EOF
import smtplib
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login('your-email@company.com', 'your-app-password')
print("SMTP connection successful")
smtp.quit()
EOF
```

## Security Hardening

### Additional Security Measures
1. **Enable fail2ban for SSH protection**
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

2. **Setup automated security updates**
```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

3. **Implement IP whitelisting for admin endpoints**
```nginx
# Add to nginx config
location /api/admin/ {
    allow 192.168.1.0/24;  # Your office IP range
    deny all;
    proxy_pass http://api_backend;
}
```

4. **Enable database connection encryption**
```bash
# Edit postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
```

## Rollback Procedure

If deployment issues occur:
```bash
# Stop services
sudo systemctl stop ar-api ar-frontend

# Restore database from backup
gunzip -c /home/ar-app/backups/ar_db_YYYYMMDD_HHMMSS.sql.gz | psql -U ar_admin -h localhost -d ar_control_hub_prod

# Revert code
cd /home/ar-app/ar-control-hub
git checkout <previous-commit-hash>
source venv/bin/activate
pip install -r requirements.txt
alembic downgrade -1

# Restart services
sudo systemctl start ar-api ar-frontend
```

## Support Contacts

- **Technical Lead:** [Name] - [email]
- **DevOps:** [Name] - [email]
- **Database Admin:** [Name] - [email]

---

**Deployment Date:** _____________
**Deployed By:** _____________
**Version:** Phase 1-3 Complete (v1.0.0)
