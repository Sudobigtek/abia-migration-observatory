#!/usr/bin/env python3
"""
NASA-LEVEL PROJECT AUDIT
Abia Migration Observatory — Stop guessing, start knowing
"""

import os
import subprocess
import sys


def run(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1


print("=" * 70)
print("  ABIA MIGRATION OBSERVATORY — PROJECT AUDIT")
print("=" * 70)

PROJECT_DIR = os.path.expanduser("~/abia-migration-observatory/abia-app")
if not os.path.exists(PROJECT_DIR):
    print(f"ERROR: {PROJECT_DIR} not found")
    sys.exit(1)

os.chdir(PROJECT_DIR)

# 1. INSTALLED_APPS audit
print("\n[1] INSTALLED_APPS AUDIT")
print("-" * 40)
stdout, _, _ = run("grep -n 'INSTALLED_APPS' abia/settings.py")
print(stdout)
stdout, _, _ = run("grep -n " "accounts" " abia/settings.py")
if stdout:
    print(f"  accounts found at: {stdout}")
else:
    print("  accounts: NOT FOUND")

# 2. App directories audit
print("\n[2] APP DIRECTORIES")
print("-" * 40)
for app in ["accounts", "migrants", "cases", "referrals", "dynamic_fields"]:
    app_dir = f"{app}"
    models_file = f"{app}/models.py"
    tests_dir = f"{app}/tests"

    status = []
    if os.path.exists(app_dir):
        status.append("dir")
        # Check ownership
        stat = os.stat(app_dir)
        owner = f"uid={stat.st_uid}"
        status.append(owner)
    else:
        status.append("MISSING")

    if os.path.exists(models_file):
        size = os.path.getsize(models_file)
        status.append(f"models.py ({size}b)")
    else:
        status.append("no models.py")

    if os.path.exists(tests_dir):
        test_files = [f for f in os.listdir(
            tests_dir) if f.startswith("test_")]
        status.append(f"tests: {len(test_files)}")
    else:
        status.append("no tests/")

    print(f"  {app:15s} | {' | '.join(status)}")

# 3. Database audit
print("\n[3] DATABASE CONNECTION")
print("-" * 40)
stdout, stderr, rc = run(
    "python manage.py dbshell -- -c 'SELECT 1;' 2>/dev/null || echo 'DB connection failed'"
)
if rc == 0:
    print("  PostgreSQL: CONNECTED")
else:
    print(f"  PostgreSQL: FAILED ({stderr[:100]})")

# 4. Migration audit
print("\n[4] MIGRATIONS")
print("-" * 40)
for app in ["accounts", "migrants", "cases", "referrals", "dynamic_fields"]:
    mig_dir = f"{app}/migrations"
    if os.path.exists(mig_dir):
        files = [
            f for f in os.listdir(mig_dir) if f.endswith(".py") and f != "__init__.py"
        ]
        print(f"  {app:15s} | {len(files)} migration(s)")
    else:
        print(f"  {app:15s} | NO migrations/")

# 5. Git status
print("\n[5] GIT STATUS")
print("-" * 40)
stdout, _, _ = run("git status --short | head -20")
if stdout:
    print(stdout)
else:
    print("  Working tree clean")

# 6. Server status
print("\n[6] SERVER STATUS")
print("-" * 40)
stdout, _, _ = run("ss -tlnp | grep ':8002 '")
if stdout:
    print(f"  Port 8002: {stdout}")
else:
    print("  Port 8002: NOT LISTENING")

print("\n" + "=" * 70)
print("  AUDIT COMPLETE")
print("=" * 70)
