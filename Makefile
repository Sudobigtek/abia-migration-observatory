# Abia Migration Observatory — Makefile
# Per Architecture Contract §19.1

.PHONY: build up down migrate test test-unit test-int lint format shell backup restore

COMPOSE := docker compose -f docker-compose.yml -f docker-compose.gateway.yml -f docker-compose.extensions.yml

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down --remove-orphans

migrate:
	$(COMPOSE) exec abia-django python manage.py migrate

test:
	$(COMPOSE) exec abia-django pytest --tb=short -q

test-unit:
	$(COMPOSE) exec abia-django pytest -m unit --tb=short -q

test-int:
	$(COMPOSE) exec abia-django pytest -m integration --tb=short -q

lint:
	$(COMPOSE) exec abia-django sh -c "black --check . && flake8 . && mypy --strict ."

format:
	$(COMPOSE) exec abia-django black .

shell:
	$(COMPOSE) exec abia-django python manage.py shell

# ── BACKUP / RESTORE (§12.3) ──

BACKUP_DIR := ./backups
BACKUP_FILE := $(BACKUP_DIR)/abia_backup_$(shell date +%Y%m%d_%H%M%S).sql

backup:
	@mkdir -p $(BACKUP_DIR)
	@echo "[BACKUP] Creating PostgreSQL dump at $(BACKUP_FILE)..."
	$(COMPOSE) exec -T abia-postgres pg_dump -U postgres -d abia_migration > $(BACKUP_FILE)
	@echo "[BACKUP] Compressing..."
	gzip -f $(BACKUP_FILE)
	@echo "[OK] Backup complete: $(BACKUP_FILE).gz"
	@ls -lh $(BACKUP_FILE).gz

restore:
	@if [ -z "$(FILE)" ]; then \
		echo "[ERROR] Usage: make restore FILE=backups/abia_backup_YYYYMMDD_HHMMSS.sql.gz"; \
		exit 1; \
	fi
	@echo "[RESTORE] Restoring from $(FILE)..."
	gunzip -c $(FILE) | $(COMPOSE) exec -T abia-postgres psql -U postgres -d abia_migration
	@echo "[OK] Restore complete"
