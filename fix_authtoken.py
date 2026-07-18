#!/usr/bin/env python3
"""
ABIA Migration Observatory — Fix: Add rest_framework.authtoken to INSTALLED_APPS
"""

import os

PROJECT_DIR = "/home/abia/abia-migration-observatory"
APP_DIR = os.path.join(PROJECT_DIR, "abia-app")
SETTINGS = os.path.join(APP_DIR, "abia", "settings.py")

print("=" * 65)
print("  FIX: Adding rest_framework.authtoken to INSTALLED_APPS")
print("=" * 65)
print()

with open(SETTINGS, "r") as f:
    content = f.read()

# Add rest_framework.authtoken after rest_framework
if "'rest_framework.authtoken'" not in content and '"rest_framework.authtoken"' not in content:
    content = content.replace(
        "    'rest_framework',",
        "    'rest_framework',\n    'rest_framework.authtoken',"
    )
    print("  Added 'rest_framework.authtoken' to INSTALLED_APPS")
else:
    print("  'rest_framework.authtoken' already in INSTALLED_APPS")

with open(SETTINGS, "w") as f:
    f.write(content)

print()
print("=" * 65)
print("  Now run migrations (to create authtoken tables), then createsuperuser:")
print("    cd /home/abia/abia-migration-observatory/abia-app")
print("    python manage.py migrate")
print("    python manage.py createsuperuser")
print()
