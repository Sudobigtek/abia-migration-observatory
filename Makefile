.PHONY: build up down migrate test shell backup restore logs lint format

build:
	cd abia-core/docker && docker compose build

up:
	cd abia-core/docker && docker compose up -d

down:
	cd abia-core/docker && docker compose down

migrate:
	cd abia-core/docker && docker compose exec django python manage.py migrate

test:
	cd abia-core/docker && docker compose exec django pytest --cov=abia --cov-report=term-missing

shell:
	cd abia-core/docker && docker compose exec django python manage.py shell

backup:
	cd abia-core/docker && docker compose exec postgres pg_dump -U postgres abia_app > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore:
	@echo "Usage: make restore FILE=backup_20260720_120000.sql"
	cd abia-core/docker && docker compose exec -T postgres psql -U postgres abia_app < $(FILE)

logs:
	cd abia-core/docker && docker compose logs -f

lint:
	cd abia-app && black . && flake8 . && mypy .

format:
	cd abia-app && black .
