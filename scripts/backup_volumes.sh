#!/bin/bash
set -e
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"
docker compose -f docker-compose.prod.yml stop web celery_worker celery_beat
docker run --rm -v abia-postgres-data:/data -v "$BACKUP_DIR:/backup" alpine tar czf /backup/postgres_${TIMESTAMP}.tar.gz -C /data .
docker run --rm -v abia-redis-data:/data -v "$BACKUP_DIR:/backup" alpine tar czf /backup/redis_${TIMESTAMP}.tar.gz -C /data .
docker run --rm -v abia-media:/data -v "$BACKUP_DIR:/backup" alpine tar czf /backup/media_${TIMESTAMP}.tar.gz -C /data .
docker compose -f docker-compose.prod.yml start web celery_worker celery_beat
echo "Done: $BACKUP_DIR/*_${TIMESTAMP}.tar.gz"
