#!/usr/bin/env python3
"""NASA Infrastructure Dashboard — Always know your stack."""
import subprocess
import json
from pathlib import Path

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

print("=" * 60)
print("  ABIA INFRASTRUCTURE DASHBOARD")
print("=" * 60)

# Docker containers
print("\n[DOCKER CONTAINERS]")
print(run("docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'"))

# Databases
print("\n[POSTGRESQL DATABASES]")
print(run("docker exec abia-postgres psql -U postgres -c \"SELECT datname FROM pg_database WHERE datistemplate = false;\" 2>/dev/null || echo 'PostgreSQL not reachable'"))

# Redis
print("\n[REDIS STATUS]")
print(run("docker exec abia-redis redis-cli ping 2>/dev/null || echo 'Redis not reachable'"))

# Django DB config
print("\n[DJANGO DATABASE CONFIG]")
print(run("cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 -B manage.py shell -c \"from django.conf import settings; print(settings.DATABASES['default'])\" 2>/dev/null || echo 'Django not configured'"))

# Port bindings
print("\n[PORT BINDINGS]")
print(run("ss -tlnp | grep -E ':(5432|6379|8000|8001)' || echo 'No relevant ports bound'"))

# .env file
env_file = Path.home() / "abia-migration-observatory" / ".env"
print(f"\n[.env FILE: {'EXISTS' if env_file.exists() else 'MISSING'}]")
if env_file.exists():
    for line in env_file.read_text().split("\n"):
        if line.strip() and not line.startswith("#"):
            key = line.split("=")[0]
            print(f"  {key}=***")

print("\n" + "=" * 60)
