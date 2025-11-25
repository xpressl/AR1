#!/bin/bash
#
# AR Control Hub - Database Backup Script
#
# This script creates compressed backups of the production database.
# Configured to run daily via cron at 2:00 AM.
#
# Features:
#   - Compressed backups (gzip)
#   - Timestamped filenames
#   - 30-day retention (auto-delete old backups)
#   - Success/failure logging
#
# Usage:
#   ./scripts/backup_database.sh
#

set -e

# Configuration
BACKUP_DIR="/var/backups/ar-control-hub"
LOG_FILE="/var/log/ar-control-hub/backup.log"
RETENTION_DAYS=30

# Database configuration (from environment or .env.production)
if [ -f "/opt/ar-control-hub/.env.production" ]; then
    export $(grep -v '^#' /opt/ar-control-hub/.env.production | grep -v '^$' | xargs)
fi

# Extract database details from DATABASE_URL
# Format: postgresql+asyncpg://user:password@host:port/database
DB_URL=${DATABASE_URL}

# Parse DATABASE_URL (handle both asyncpg and psycopg2 formats)
DB_URL_CLEAN=$(echo "$DB_URL" | sed 's/postgresql+asyncpg/postgresql/' | sed 's/postgresql+psycopg2/postgresql/')

# Extract credentials
DB_USER=$(echo "$DB_URL_CLEAN" | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASSWORD=$(echo "$DB_URL_CLEAN" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_HOST=$(echo "$DB_URL_CLEAN" | sed -n 's|.*@\([^:]*\):.*|\1|p')
DB_PORT=$(echo "$DB_URL_CLEAN" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
DB_NAME=$(echo "$DB_URL_CLEAN" | sed -n 's|.*/\([^?]*\).*|\1|p')

# Defaults if not found
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-ar_control_hub_prod}

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_READABLE=$(date '+%Y-%m-%d %H:%M:%S')

# Backup filename
BACKUP_FILE="$BACKUP_DIR/ar_prod_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create log file if it doesn't exist
touch $LOG_FILE

echo "[$DATE_READABLE] Starting database backup..." >> $LOG_FILE

# Perform backup
export PGPASSWORD=$DB_PASSWORD

if pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT $DB_NAME > $BACKUP_FILE 2>> $LOG_FILE; then
    # Compress backup
    gzip $BACKUP_FILE

    # Get compressed file size
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)

    echo "[$DATE_READABLE] ✓ Backup successful: ${BACKUP_FILE}.gz ($SIZE)" >> $LOG_FILE

    # Delete backups older than retention period
    DELETED_COUNT=$(find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)

    if [ $DELETED_COUNT -gt 0 ]; then
        echo "[$DATE_READABLE] Deleted $DELETED_COUNT old backup(s) (older than $RETENTION_DAYS days)" >> $LOG_FILE
    fi

    # List current backups
    BACKUP_COUNT=$(find $BACKUP_DIR -name "*.sql.gz" | wc -l)
    echo "[$DATE_READABLE] Total backups: $BACKUP_COUNT" >> $LOG_FILE

    exit 0
else
    echo "[$DATE_READABLE] ✗ Backup FAILED - Check PostgreSQL connectivity" >> $LOG_FILE

    # Send alert (configure your alerting mechanism here)
    # Example: send email, Slack notification, PagerDuty alert, etc.
    # mail -s "AR Control Hub Backup FAILED" admin@company.com < $LOG_FILE

    exit 1
fi

unset PGPASSWORD
