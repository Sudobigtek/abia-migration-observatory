#!/usr/bin/env python3
"""
ABIA Test Environment Quick Fix — Python Version
Run this from your project root: python3 fix_tests.py
"""

import os
import subprocess
import sys


def run(cmd, check=True):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"ERROR: {cmd}\n{result.stderr}")
        return None
    return result.stdout.strip()


def main():
    print("=" * 50)
    print("ABIA TEST ENVIRONMENT FIX (Python)")
    print("=" * 50)

    # Detect if we're inside Docker
    in_docker = os.path.exists("/.dockerenv")
    print(f"\n[1] Environment: {'Docker' if in_docker else 'WSL/Host'}")

    # Check postgres container
    pg_running = "abia-postgres" in (
        run("docker ps --format '{{.Names}}'", check=False) or ""
    )
    print(f"[2] PostgreSQL container: {'RUNNING ✓' if pg_running else 'NOT RUNNING ✗'}")

    # Determine host
    host = "postgres" if in_docker else "localhost"
    print(f"[3] Database host: {host}")

    # Create test_settings.py
    app_dir = os.path.join(os.getcwd(), "abia-app")
    abia_dir = os.path.join(app_dir, "abia")
    os.makedirs(abia_dir, exist_ok=True)

    test_settings_path = os.path.join(abia_dir, "test_settings.py")
    with open(test_settings_path, "w") as f:
        f.write(f"""from .settings import *

DATABASES = {{
    'default': {{
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('POSTGRES_DB', 'abia_app_test'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'changeme'),
        'HOST': os.getenv('POSTGRES_HOST', '{host}'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }}
}}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
CELERY_TASK_ALWAYS_EAGER = True
CACHES = {{'default': {{'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}}}
""")
    print(f"[4] Created: {test_settings_path}")

    # Create pytest.ini
    pytest_ini = os.path.join(app_dir, "pytest.ini")
    with open(pytest_ini, "w") as f:
        f.write("""[pytest]
DJANGO_SETTINGS_MODULE = abia.test_settings
python_files = tests.py test_*.py *_tests.py
addopts = -v --tb=short --reuse-db
""")
    print(f"[5] Created: {pytest_ini}")

    # Create test database
    if pg_running and not in_docker:
        print("[6] Creating test database...")
        run(
            "docker exec abia-postgres psql -U postgres -c 'CREATE DATABASE abia_app_test;' 2>/dev/null || true",
            check=False,
        )
        print("     ✓ Test database ready")

    print("\n" + "=" * 50)
    print("FIX COMPLETE!")
    print("=" * 50)
    print("\nRun tests with:")
    print("  cd abia-app && pytest")
    print("\nOr with explicit settings:")
    print("  cd abia-app && DJANGO_SETTINGS_MODULE=abia.test_settings pytest")
    print("\nFor even faster tests:")
    print("  cd abia-app && pytest --reuse-db --no-migrations -x")


if __name__ == "__main__":
    main()
