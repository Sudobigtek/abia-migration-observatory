#!/usr/bin/env python3
"""
ABIA Migration Observatory — PATH A FIX v3
Adds missing root-level apps (dynamic_fields) to INSTALLED_APPS.
"""

import os

PROJECT_DIR = "/home/abia/abia-migration-observatory"
APP_DIR = os.path.join(PROJECT_DIR, "abia-app")
SETTINGS = os.path.join(APP_DIR, "abia", "settings.py")

# DISCOVER ALL APPS (both abia/ and root-level)
all_apps = []

# Check abia/ subdirectory
abia_apps_dir = os.path.join(APP_DIR, "abia")
if os.path.isdir(abia_apps_dir):
    for name in os.listdir(abia_apps_dir):
        app_path = os.path.join(abia_apps_dir, name)
        if os.path.isdir(app_path) and os.path.exists(os.path.join(app_path, "__init__.py")):
            all_apps.append("abia." + name)

# Check root-level apps (like dynamic_fields)
for name in os.listdir(APP_DIR):
    app_path = os.path.join(APP_DIR, name)
    if os.path.isdir(app_path) and os.path.exists(os.path.join(app_path, "__init__.py")):
        # Skip django project dirs and common non-app dirs
        if name in ['abia', 'templates', 'static', 'media', 'staticfiles', '__pycache__', 'migrations']:
            continue
        # Check if it looks like a Django app (has models.py or apps.py)
        if os.path.exists(os.path.join(app_path, "models.py")) or \
           os.path.exists(os.path.join(app_path, "apps.py")):
            all_apps.append(name)

print("=" * 65)
print("  ABIA PATH A — FIX v3: DISCOVER ALL APPS")
print("=" * 65)
print()
print("  Discovered apps: " + str(sorted(all_apps)))
print()

# Read current settings.py
with open(SETTINGS, "r") as f:
    content = f.read()

# Find and replace INSTALLED_APPS
import re

# Build new INSTALLED_APPS block
base_apps = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "corsheaders",
]

all_apps_sorted = base_apps + sorted(all_apps)
apps_lines = ["    '" + a + "'," for a in all_apps_sorted]
new_installed_apps = "INSTALLED_APPS = [\n" + "\n".join(apps_lines) + "\n]"

# Replace the INSTALLED_APPS block in settings.py
pattern = r"INSTALLED_APPS = \[.*?\]"
content_new = re.sub(pattern, new_installed_apps, content, flags=re.DOTALL)

with open(SETTINGS, "w") as f:
    f.write(content_new)

print("[1/1] Updated settings.py with all discovered apps")
print("  OK INSTALLED_APPS now includes: " + ", ".join(sorted(all_apps)))
print()
print("=" * 65)
print("  Now run:")
print("    cd /home/abia/abia-migration-observatory/abia-app")
print("    python manage.py migrate")
print()
