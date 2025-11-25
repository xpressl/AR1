# AR Control Hub - Production Runbook

**Last Updated:** ________________
**Version:** 1.0.0
**Environment:** Production

---

## Quick Reference

| Item | Details |
|------|---------|
| **Production URL** | https://ar.company.com |
| **Server IP** | [IP_ADDRESS] |
| **SSH Access** | `ssh arapp@ar.company.com` |
| **Application Dir** | `/opt/ar-control-hub` |
| **Log Directory** | `/var/log/ar-control-hub/` |
| **Backup Directory** | `/var/backups/ar-control-hub/` |

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Common Operations](#common-operations)
3. [Service Management](#service-management)
4. [Monitoring](#monitoring)
5. [Backup & Restore](#backup--restore)
6. [Troubleshooting](#troubleshooting)
7. [Deployment](#deployment)
8. [Security](#security)
9. [Performance Tuning](#performance-tuning)
10. [Disaster Recovery](#disaster-recovery)

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Nginx (443)   │  SSL/TLS Termination
                    │  Reverse Proxy │  Load Balancing
                    └───────┬────────┘
                            │
            ┌───────────────┴────────────────┐
            │                                │
    ┌───────▼────────┐             ┌────────▼─────────┐
    │  Frontend      │             │  Backend API     │
    │  Next.js       │             │  FastAPI         │
    │  (Port 3000)   │             │  (Port 8000)     │
    └───────┬────────┘             └────────┬─────────┘
            │                               │
            └───────────────┬───────────────┘
                            │
                    ┌───────▼────────┐
                    │  PostgreSQL    │
                    │  (Port 5432)   │
                    └────────────────┘
```

### Services

| Service | Description | Port | Systemd Unit |
|---------|-------------|------|--------------|
| Nginx | Web server & reverse proxy | 80, 443 | nginx.service |
| Backend API | FastAPI application | 8000 | ar-backend.service |
| Frontend | Next.js application | 3000 | ar-frontend.service |
| PostgreSQL | Database | 5432 | postgresql.service |

---

## Common Operations

### Checking System Status

```bash
# Quick health check
curl https://ar.company.com/health

# Check all services
systemctl status ar-backend ar-frontend nginx postgresql

# Run comprehensive health check
/opt/ar-control-hub/scripts/health_check.sh
```

### Viewing Logs

```bash
# Backend application logs
tail -f /var/log/ar-control-hub/app.log

# Backend error logs
tail -f /var/log/ar-control-hub/error.log

# Backend access logs
tail -f /var/log/ar-control-hub/access.log

# Backend systemd logs (last 100 lines)
journalctl -u ar-backend -n 100 --no-pager

# Backend systemd logs (live follow)
journalctl -u ar-frontend -f

# Nginx access logs
tail -f /var/log/nginx/ar-control-hub-access.log

# Nginx error logs
tail -f /var/log/nginx/ar-control-hub-error.log

# PostgreSQL logs
tail -f /var/log/postgresql/postgresql-14-main.log

# Health check logs
tail -f /var/log/ar-control-hub/health_check.log

# Backup logs
tail -f /var/log/ar-control-hub/backup.log
```

### Checking Database

```bash
# Connect to database
sudo -u postgres psql -d ar_control_hub_prod

# Check database size
psql -d ar_control_hub_prod -c "SELECT pg_size_pretty(pg_database_size('ar_control_hub_prod'));"

# Count records
psql -d ar_control_hub_prod -c "
SELECT
    'customers' as table, COUNT(*) FROM customers
UNION ALL
    SELECT 'invoices', COUNT(*) FROM invoices
UNION ALL
    SELECT 'payments', COUNT(*) FROM payments
UNION ALL
    SELECT 'users', COUNT(*) FROM users;
"

# Check for slow queries
psql -d ar_control_hub_prod -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check active connections
psql -d ar_control_hub_prod -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';"
```

### Checking Server Resources

```bash
# CPU usage
top -bn1 | head -20

# Memory usage
free -h

# Disk usage
df -h

# Disk I/O
iostat -x 1 5

# Network connections
netstat -tuln | grep -E ':8000|:3000|:5432|:443'

# Process list for AR services
ps aux | grep -E 'uvicorn|npm|postgres'
```

---

## Service Management

### Backend API (ar-backend.service)

```bash
# Start backend
sudo systemctl start ar-backend

# Stop backend
sudo systemctl stop ar-backend

# Restart backend
sudo systemctl restart ar-backend

# Reload backend (graceful restart)
sudo systemctl reload ar-backend

# Check status
sudo systemctl status ar-backend

# Enable auto-start on boot
sudo systemctl enable ar-backend

# Disable auto-start
sudo systemctl disable ar-backend

# View logs (last 50 lines)
sudo journalctl -u ar-backend -n 50 --no-pager

# View logs (live follow)
sudo journalctl -u ar-backend -f
```

### Frontend (ar-frontend.service)

```bash
# Start frontend
sudo systemctl start ar-frontend

# Stop frontend
sudo systemctl stop ar-frontend

# Restart frontend
sudo systemctl restart ar-frontend

# Check status
sudo systemctl status ar-frontend

# View logs
sudo journalctl -u ar-frontend -n 50 --no-pager
```

### Nginx

```bash
# Start Nginx
sudo systemctl start nginx

# Stop Nginx
sudo systemctl stop nginx

# Restart Nginx
sudo systemctl restart nginx

# Reload Nginx (graceful, no downtime)
sudo systemctl reload nginx

# Test configuration
sudo nginx -t

# Check status
sudo systemctl status nginx
```

### PostgreSQL

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Stop PostgreSQL
sudo systemctl stop postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Reload configuration (no restart)
sudo systemctl reload postgresql

# Check status
sudo systemctl status postgresql

# Check if accepting connections
sudo -u postgres psql -c "SELECT version();"
```

### Restart All Services (Rolling Restart)

```bash
# Restart in correct order (minimal downtime)
sudo systemctl restart postgresql  # Database first
sleep 5
sudo systemctl restart ar-backend   # Backend second
sleep 5
sudo systemctl restart ar-frontend  # Frontend third
sudo systemctl reload nginx         # Nginx last (graceful reload)

# Verify all healthy
/opt/ar-control-hub/scripts/health_check.sh
```

---

## Monitoring

### Health Checks

```bash
# Manual health check
/opt/ar-control-hub/scripts/health_check.sh

# Check health check cron job
crontab -u arapp -l | grep health_check

# View health check history
tail -100 /var/log/ar-control-hub/health_check.log
```

### Performance Metrics

```bash
# Backend API response time
curl -o /dev/null -s -w "Time: %{time_total}s\nHTTP Code: %{http_code}\n" https://ar.company.com/api/v1/dashboard/summary

# Database query performance
psql -d ar_control_hub_prod -c "
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_time DESC
LIMIT 20;
"

# Active database connections
psql -d ar_control_hub_prod -c "
SELECT
    datname,
    count(*) as connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle
FROM pg_stat_activity
WHERE datname IS NOT NULL
GROUP BY datname;
"
```

### Log Monitoring

```bash
# Count errors in last hour
grep -i error /var/log/ar-control-hub/app.log | grep "$(date -u +%Y-%m-%d)" | tail -100

# Find 500 errors in Nginx
grep " 500 " /var/log/nginx/ar-control-hub-access.log | tail -20

# Find slow queries
grep "slow query" /var/log/ar-control-hub/app.log | tail -20
```

---

## Backup & Restore

### Manual Backup

```bash
# Run manual backup
/opt/ar-control-hub/scripts/backup_database.sh

# Verify backup created
ls -lh /var/backups/ar-control-hub/

# Check backup log
tail -20 /var/log/ar-control-hub/backup.log
```

### Automated Backups

```bash
# Check backup cron job
crontab -u arapp -l | grep backup_database

# Expected: 0 2 * * * /opt/ar-control-hub/scripts/backup_database.sh

# List all backups
ls -lh /var/backups/ar-control-hub/

# Count backups
ls -1 /var/backups/ar-control-hub/*.sql.gz | wc -l

# Find oldest backup
ls -lt /var/backups/ar-control-hub/*.sql.gz | tail -1

# Find newest backup
ls -lt /var/backups/ar-control-hub/*.sql.gz | head -1
```

### Restore from Backup

```bash
# CAUTION: This will overwrite the production database!

# 1. Stop backend to prevent writes
sudo systemctl stop ar-backend

# 2. List available backups
ls -lt /var/backups/ar-control-hub/

# 3. Choose backup to restore
BACKUP_FILE="/var/backups/ar-control-hub/ar_prod_backup_YYYYMMDD_HHMMSS.sql.gz"

# 4. Create database backup before restore (safety)
pg_dump -U ar_admin -d ar_control_hub_prod | gzip > /tmp/pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# 5. Drop all connections to database
psql -U postgres -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'ar_control_hub_prod'
  AND pid <> pg_backend_pid();
"

# 6. Restore backup
gunzip -c $BACKUP_FILE | psql -U ar_admin -d ar_control_hub_prod

# 7. Verify restore
psql -d ar_control_hub_prod -c "SELECT COUNT(*) FROM customers;"

# 8. Start backend
sudo systemctl start ar-backend

# 9. Verify application works
curl https://ar.company.com/health
```

### Test Restore (Safe)

```bash
# Create temporary test database
psql -U postgres -c "CREATE DATABASE ar_test_restore;"

# Restore latest backup to test database
LATEST_BACKUP=$(ls -t /var/backups/ar-control-hub/*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | psql -U postgres -d ar_test_restore

# Verify data
psql -d ar_test_restore -c "SELECT COUNT(*) FROM customers;"

# Cleanup
psql -U postgres -c "DROP DATABASE ar_test_restore;"
```

---

## Troubleshooting

### Backend API Not Responding

**Symptoms:**
- `curl https://ar.company.com/health` returns 502 Bad Gateway
- `systemctl status ar-backend` shows "active (running)" but not responding

**Diagnosis:**
```bash
# Check if backend process is running
ps aux | grep uvicorn

# Check backend logs for errors
journalctl -u ar-backend -n 100 --no-pager | grep -i error

# Check if port 8000 is listening
netstat -tuln | grep :8000

# Test backend directly (bypass Nginx)
curl http://localhost:8000/health
```

**Solutions:**
```bash
# Solution 1: Restart backend
sudo systemctl restart ar-backend
sleep 5
curl http://localhost:8000/health

# Solution 2: Check database connection
psql -U ar_admin -d ar_control_hub_prod -c "SELECT 1;"

# Solution 3: Check environment variables
sudo grep -v '^#' /opt/ar-control-hub/.env.production | grep DATABASE_URL

# Solution 4: Check disk space
df -h

# Solution 5: Check memory
free -h

# Solution 6: View detailed logs
journalctl -u ar-backend -n 200 --no-pager
```

### Frontend Not Loading

**Symptoms:**
- Browser shows "This site can't be reached"
- Nginx returns 502 Bad Gateway for frontend

**Diagnosis:**
```bash
# Check frontend service
systemctl status ar-frontend

# Check if port 3000 is listening
netstat -tuln | grep :3000

# Test frontend directly
curl http://localhost:3000

# Check frontend logs
journalctl -u ar-frontend -n 100 --no-pager
```

**Solutions:**
```bash
# Solution 1: Restart frontend
sudo systemctl restart ar-frontend

# Solution 2: Rebuild frontend
cd /opt/ar-control-hub
sudo -u arapp npm run build
sudo systemctl restart ar-frontend

# Solution 3: Check Node.js
node --version
npm --version
```

### Database Connection Errors

**Symptoms:**
- Backend logs show "could not connect to database"
- API returns 500 Internal Server Error

**Diagnosis:**
```bash
# Check PostgreSQL service
systemctl status postgresql

# Check PostgreSQL logs
tail -50 /var/log/postgresql/postgresql-14-main.log

# Check database connections
psql -d ar_control_hub_prod -c "SELECT count(*) FROM pg_stat_activity;"

# Test connection manually
psql -U ar_admin -d ar_control_hub_prod -c "SELECT version();"
```

**Solutions:**
```bash
# Solution 1: Restart PostgreSQL
sudo systemctl restart postgresql

# Solution 2: Check max connections
psql -d ar_control_hub_prod -c "SHOW max_connections;"

# Solution 3: Kill idle connections
psql -d ar_control_hub_prod -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < current_timestamp - INTERVAL '1 hour';
"

# Solution 4: Check disk space
df -h
```

### Slow Performance

**Symptoms:**
- API requests taking > 5 seconds
- Database queries slow
- High CPU/memory usage

**Diagnosis:**
```bash
# Check server resources
top -bn1 | head -20
free -h
iostat -x 1 5

# Find slow database queries
psql -d ar_control_hub_prod -c "
SELECT
    pid,
    now() - query_start as duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
"

# Check backend worker count
ps aux | grep uvicorn | wc -l

# Test API response time
time curl -s https://ar.company.com/api/v1/dashboard/summary > /dev/null
```

**Solutions:**
```bash
# Solution 1: Restart services (clears memory)
sudo systemctl restart ar-backend ar-frontend

# Solution 2: Vacuum database
psql -d ar_control_hub_prod -c "VACUUM ANALYZE;"

# Solution 3: Clear old data (if applicable)
# (Create cleanup script for old records)

# Solution 4: Increase backend workers
# Edit /etc/systemd/system/ar-backend.service
# Change --workers 4 to --workers 8
sudo systemctl daemon-reload
sudo systemctl restart ar-backend
```

### SSL Certificate Expired

**Symptoms:**
- Browser shows "Your connection is not private"
- Certificate expired error

**Diagnosis:**
```bash
# Check certificate expiration
sudo certbot certificates
```

**Solutions:**
```bash
# Renew certificate
sudo certbot renew

# Reload Nginx
sudo systemctl reload nginx

# Test HTTPS
curl -I https://ar.company.com
```

### Disk Space Full

**Symptoms:**
- Services failing to start
- Cannot create files
- Database errors

**Diagnosis:**
```bash
# Check disk usage
df -h

# Find largest directories
du -h / | sort -rh | head -20

# Find largest files
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | head -20
```

**Solutions:**
```bash
# Solution 1: Clean old logs
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.gz" -mtime +30 -delete

# Solution 2: Clean old backups (older than 60 days)
sudo find /var/backups/ar-control-hub -name "*.sql.gz" -mtime +60 -delete

# Solution 3: Clean package cache
sudo apt clean

# Solution 4: Remove old kernels
sudo apt autoremove
```

---

## Deployment

### Deploying Code Updates

```bash
# 1. SSH to production server
ssh arapp@ar.company.com

# 2. Navigate to application directory
cd /opt/ar-control-hub

# 3. Create backup before deployment
/opt/ar-control-hub/scripts/backup_database.sh

# 4. Pull latest code
git fetch origin
git checkout v1.0.1  # Replace with your version tag

# 5. Install/update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 6. Run database migrations
export $(grep -v '^#' .env.production | xargs)
alembic upgrade head

# 7. Rebuild frontend
npm install --production
npm run build

# 8. Restart services
sudo systemctl restart ar-backend
sleep 5
sudo systemctl restart ar-frontend

# 9. Verify deployment
curl https://ar.company.com/health
/opt/ar-control-hub/scripts/health_check.sh

# 10. Monitor logs for errors
tail -f /var/log/ar-control-hub/error.log
```

### Rolling Back Deployment

```bash
# 1. Checkout previous version
cd /opt/ar-control-hub
git checkout v1.0.0  # Previous stable version

# 2. Restore database backup (if migrations were run)
BACKUP_FILE=$(ls -t /var/backups/ar-control-hub/*.sql.gz | head -1)
gunzip -c $BACKUP_FILE | psql -U ar_admin -d ar_control_hub_prod

# 3. Downgrade database (if migrations were run)
source venv/bin/activate
alembic downgrade -1  # Go back one migration

# 4. Restart services
sudo systemctl restart ar-backend
sudo systemctl restart ar-frontend

# 5. Verify
curl https://ar.company.com/health
```

---

## Security

### Security Checklist

```bash
# Check firewall status
sudo ufw status verbose

# Check Fail2Ban status
sudo fail2ban-client status sshd

# Check file permissions
ls -la /opt/ar-control-hub/.env.production
# Should be: -rw------- (600)

# Check for security updates
sudo apt update
sudo apt list --upgradable | grep -i security

# Check SSL certificate
sudo certbot certificates

# Check open ports
sudo netstat -tuln | grep LISTEN

# Check for unauthorized SSH keys
cat ~/.ssh/authorized_keys

# Review user accounts
cat /etc/passwd | grep -v nologin
```

### Updating Security

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Update Python packages
cd /opt/ar-control-hub
source venv/bin/activate
pip install --upgrade pip
pip list --outdated

# Update Node packages
npm outdated
npm update

# Renew SSL certificate
sudo certbot renew
```

---

## Performance Tuning

### Database Optimization

```bash
# Analyze query performance
psql -d ar_control_hub_prod -c "
SELECT
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"

# Vacuum and analyze
psql -d ar_control_hub_prod -c "VACUUM ANALYZE;"

# Reindex
psql -d ar_control_hub_prod -c "REINDEX DATABASE ar_control_hub_prod;"

# Update statistics
psql -d ar_control_hub_prod -c "ANALYZE;"
```

### Backend Tuning

```bash
# Adjust worker count based on CPU cores
# Edit /etc/systemd/system/ar-backend.service
# Formula: workers = (2 x CPU_cores) + 1

# For 4 CPU cores: --workers 9
# For 8 CPU cores: --workers 17

sudo systemctl daemon-reload
sudo systemctl restart ar-backend
```

---

## Disaster Recovery

### Complete System Failure

**Recovery Steps:**

1. **Provision new server** with same specs
2. **Install prerequisites** (PostgreSQL, Python, Node.js, Nginx)
3. **Restore latest backup:**
   ```bash
   # Copy backup from backup server/S3
   scp backup-server:/backups/latest.sql.gz /tmp/

   # Create database
   createdb ar_control_hub_prod

   # Restore
   gunzip -c /tmp/latest.sql.gz | psql -d ar_control_hub_prod
   ```
4. **Deploy application** using deployment script
5. **Configure Nginx** and SSL certificate
6. **Update DNS** to point to new server
7. **Verify** all services working

**Recovery Time Objective (RTO):** 4 hours
**Recovery Point Objective (RPO):** 24 hours (daily backups)

---

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| System Administrator | [Name] | [Phone] | [Email] |
| Database Administrator | [Name] | [Phone] | [Email] |
| Application Owner | [Name] | [Phone] | [Email] |
| IT Manager | [Name] | [Phone] | [Email] |
| On-Call Rotation | [Link] | [Phone] | [Email] |

---

## Appendix

### Useful Commands Reference

```bash
# Quick health check
curl -s https://ar.company.com/health | jq

# Restart all services
for service in postgresql ar-backend ar-frontend nginx; do sudo systemctl restart $service; sleep 5; done

# View all logs (last 100 lines)
for log in app.log access.log error.log; do echo "=== $log ===" && tail -100 /var/log/ar-control-hub/$log; done

# Database backup
/opt/ar-control-hub/scripts/backup_database.sh

# Database restore
gunzip -c BACKUP_FILE.sql.gz | psql -U ar_admin -d ar_control_hub_prod

# Check system resources
echo "CPU:"; top -bn1 | grep "Cpu(s)"; echo "MEM:"; free -h; echo "DISK:"; df -h /
```

---

**Last Reviewed:** ________________
**Next Review Date:** ________________
**Reviewed By:** ________________
