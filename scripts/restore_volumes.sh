#!/bin/bash
set -e
if [ -z "$1" ]; then echo "Usage: $0 <timestamp>"; exit 1; fi
TIMESTAMP=$1; BACKUP_DIR="${BACKUP_DIR:-./backups}"
read -p "Overwrite existing data? (yes/no): " confirm
[ "$confirm" != "yes" ] && echo "Aborted." && exit 1
docker run --rm -v abia-postgres-data:/data -v "$BACKUP_DIR:/backup" alpine sh -c "cd /data && tar xzf /backup/postgres_${TIMESTAMP}.tar.gz"
docker run --rm -v abia-redis-data:/data -v "$BACKUP_DIR:/backup" alpine sh -c "cd /data && tar xzf /backup/redis_${TIMESTAMP}.tar.gz"
docker run --rm -v abia-media:/data -v "$BACKUP_DIR:/backup" alpine sh -c "cd /data && tar xzf /backup/media_${TIMESTAMP}.tar.gz"
echo "Done. Start: docker compose -f docker-compose.prod.yml up -d"
