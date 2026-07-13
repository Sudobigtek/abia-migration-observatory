#!/bin/bash
# Automated PostgreSQL backup — add to crontab

set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="abia_backup_${DATE}.sql"
S3_BUCKET="abia-migration-backups"
RETENTION_DAYS=30

echo "[$(date)] Starting backup..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Dump database
docker compose exec -T postgres pg_dump -U postgres abia_app > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress
gzip ${BACKUP_DIR}/${BACKUP_FILE}

# Encrypt with GPG
gpg --symmetric --cipher-algo AES256 --batch --passphrase-file /run/secrets/postgres_password     ${BACKUP_DIR}/${BACKUP_FILE}.gz

# Upload to S3 (if configured)
if command -v aws &> /dev/null; then
    aws s3 cp ${BACKUP_DIR}/${BACKUP_FILE}.gz.gpg s3://${S3_BUCKET}/
    echo "[$(date)] Uploaded to S3: ${BACKUP_FILE}.gz.gpg"
fi

# Publish to IPFS for decentralized backup
CID=$(docker compose exec -T ipfs ipfs add -q /dev/stdin < ${BACKUP_DIR}/${BACKUP_FILE}.gz.gpg)
echo "[$(date)] IPFS CID: ${CID}" >> /var/log/abia-backups.log

# Cleanup old backups
find $BACKUP_DIR -name "abia_backup_*.sql*" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Backup complete: ${BACKUP_FILE}.gz.gpg"
