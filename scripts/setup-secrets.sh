#!/bin/bash
# Production secrets setup — run from WSL host

set -e

echo "=== ABIA MIGRATION OBSERVATORY — SECRETS SETUP ==="

# Generate secure passwords if not provided
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$(openssl rand -base64 32)}
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY:-$(openssl rand -base64 50)}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-$(openssl rand -base64 16)}

echo "Creating Docker secrets..."

# Remove old secrets if they exist (ignore errors)
docker secret rm postgres_password 2>/dev/null || true
docker secret rm django_secret_key 2>/dev/null || true
docker secret rm grafana_password 2>/dev/null || true

# Create new secrets
echo "$POSTGRES_PASSWORD" | docker secret create postgres_password -
echo "$DJANGO_SECRET_KEY" | docker secret create django_secret_key -
echo "$GRAFANA_PASSWORD" | docker secret create grafana_password -

echo ""
echo "Secrets created successfully."
echo ""
echo "Postgres Password: $POSTGRES_PASSWORD"
echo "Django Secret Key: $DJANGO_SECRET_KEY"
echo "Grafana Password:  $GRAFANA_PASSWORD"
echo ""
echo "SAVE THESE IN YOUR PASSWORD MANAGER (Bitwarden)."
echo "They will not be displayed again."
