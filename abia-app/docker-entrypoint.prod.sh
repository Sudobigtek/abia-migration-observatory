#!/bin/bash
set -e

# Wait for postgres
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput 2>/dev/null || true

# Start gunicorn
exec gunicorn abia.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --worker-class gthread \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance
