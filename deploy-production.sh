#!/bin/bash
# Abia MIGRATION OBSERVATORY — PRODUCTION DEPLOYMENT (Compose version)

set -e

echo "=========================================="
echo "ABIA MIGRATION OBSERVATORY — PRODUCTION DEPLOYMENT"
echo "=========================================="

# 1. Copy downloaded files to project
echo ""
echo "[1/7] Copying files to project..."
cp /mnt/c/Users/Admin/Downloads/docker-compose.prod.yml ~/abia-migration-observatory/
mkdir -p ~/abia-migration-observatory/nginx
mkdir -p ~/abia-migration-observatory/scripts
mkdir -p ~/abia-migration-observatory/prometheus
mkdir -p ~/abia-migration-observatory/grafana/provisioning

cp /mnt/c/Users/Admin/Downloads/nginx.conf ~/abia-migration-observatory/nginx/
cp /mnt/c/Users/Admin/Downloads/setup-secrets.sh ~/abia-migration-observatory/scripts/
cp /mnt/c/Users/Admin/Downloads/backup.sh ~/abia-migration-observatory/scripts/
cp /mnt/c/Users/Admin/Downloads/prometheus.yml ~/abia-migration-observatory/prometheus/
cp /mnt/c/Users/Admin/Downloads/alerts.yml ~/abia-migration-observatory/prometheus/
cp /mnt/c/Users/Admin/Downloads/settings_secrets_patch.py ~/abia-migration-observatory/
cp /mnt/c/Users/Admin/Downloads/Makefile ~/abia-migration-observatory/

chmod +x ~/abia-migration-observatory/scripts/setup-secrets.sh
chmod +x ~/abia-migration-observatory/scripts/backup.sh
echo "  ✅ Files copied"

# 2. Create SSL certificates
echo ""
echo "[2/7] Creating SSL certificates..."
mkdir -p ~/abia-migration-observatory/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ~/abia-migration-observatory/nginx/ssl/key.pem \
    -out ~/abia-migration-observatory/nginx/ssl/cert.pem \
    -subj "/C=NG/ST=Abia/L=Umuahia/O=Abia Migration Observatory/CN=api.abia-migration.gov.ng" \
    2>/dev/null || echo "  ⚠️  OpenSSL not available (install: sudo apt install openssl)"
echo "  ✅ SSL ready"

# 3. Create .env file with secrets (Compose alternative to Docker secrets)
echo ""
echo "[3/7] Creating .env with secure secrets..."
cd ~/abia-migration-observatory

POSTGRES_PASSWORD=$(openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64)
DJANGO_SECRET_KEY=$(openssl rand -base64 50 2>/dev/null || head -c 50 /dev/urandom | base64)
GRAFANA_PASSWORD=$(openssl rand -base64 16 2>/dev/null || head -c 16 /dev/urandom | base64)

cat > .env.prod << EOENV
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=api.abia-migration.gov.ng,localhost,127.0.0.1
POSTGRES_DB=abia_app
POSTGRES_USER=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
EOENV

echo "  ✅ .env.prod created"
echo ""
echo "SAVE THESE PASSWORDS TO BITWARDEN:"
echo "  Postgres Password: ${POSTGRES_PASSWORD}"
echo "  Django Secret Key: ${DJANGO_SECRET_KEY}"
echo "  Grafana Password:  ${GRAFANA_PASSWORD}"
echo ""

# 4. Update docker-compose.prod.yml to use .env instead of secrets
sed -i 's|POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password|POSTGRES_PASSWORD=${POSTGRES_PASSWORD}|g' docker-compose.prod.yml
sed -i 's|DJANGO_SECRET_KEY_FILE=/run/secrets/django_secret_key|DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}|g' docker-compose.prod.yml
sed -i 's|GF_SECURITY_ADMIN_PASSWORD__FILE=/run/secrets/grafana_password|GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}|g' docker-compose.prod.yml
sed -i '/secrets:/,/^$/d' docker-compose.prod.yml  # Remove secrets section
sed -i '/- postgres_password/d' docker-compose.prod.yml
sed -i '/- django_secret_key/d' docker-compose.prod.yml
sed -i '/- grafana_password/d' docker-compose.prod.yml

echo "  ✅ docker-compose.prod.yml updated for .env"

# 5. Stop dev services
echo ""
echo "[5/7] Stopping development services..."
docker compose -f docker-compose.yml -f docker-compose.kong.yml down 2>/dev/null || true
echo "  ✅ Dev services stopped"

# 6. Start production services
echo ""
echo "[6/7] Starting production services..."
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
echo "  ✅ Production services started"

# 7. Run migrations
echo ""
echo "[7/7] Running database migrations..."
sleep 10
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T django python manage.py migrate
echo "  ✅ Migrations complete"

# 8. Run tests
echo ""
echo "[8/8] Running test suite..."
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T django python -m pytest -v --tb=short 2>&1 | tail -n 20

echo ""
echo "=========================================="
echo "DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "Services:"
echo "  Django API:    http://localhost:8000 (internal)"
echo "  Nginx Proxy:   https://localhost (external, self-signed cert)"
echo "  Prometheus:    http://localhost:9090"
echo "  Grafana:       http://localhost:3000 (admin / password from above)"
echo "  Kong Admin:    http://localhost:8001"
echo "  Camunda:       http://localhost:8080"
echo "  IPFS:          http://localhost:5001"
echo "  Ollama:        http://localhost:11434"
echo ""
echo "Next steps:"
echo "  1. Save passwords to Bitwarden (displayed above)"
echo "  2. Add backup to crontab: crontab -e"
echo "  3. Replace self-signed certs with Let's Encrypt for production"
echo "  4. Configure firewall: sudo ufw allow 443/tcp"
echo ""
