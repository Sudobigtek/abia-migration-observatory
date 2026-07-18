#!/usr/bin/env python3
"""
ABIA Migration Observatory — PATH A FIX v4
Adds AUTH_USER_MODEL and django.contrib.postgres to settings.py
"""

import os
import re

PROJECT_DIR = "/home/abia/abia-migration-observatory"
APP_DIR = os.path.join(PROJECT_DIR, "abia-app")
SETTINGS = os.path.join(APP_DIR, "abia", "settings.py")

print("=" * 65)
print("  ABIA PATH A — FIX v4")
print("  Adding AUTH_USER_MODEL + django.contrib.postgres")
print("=" * 65)
print()

with open(SETTINGS, "r") as f:
    content = f.read()

# 1. Add django.contrib.postgres to INSTALLED_APPS if missing
if "'django.contrib.postgres'" not in content and '"django.contrib.postgres"' not in content:
    # Insert after django.contrib.gis
    content = content.replace(
        "    'django.contrib.gis',",
        "    'django.contrib.gis',\n    'django.contrib.postgres',"
    )
    print("[1/2] Added 'django.contrib.postgres' to INSTALLED_APPS")
else:
    print("[1/2] 'django.contrib.postgres' already in INSTALLED_APPS")

# 2. Add AUTH_USER_MODEL if missing
if "AUTH_USER_MODEL" not in content:
    # Find a good place to insert — after INSTALLED_APPS block, before MIDDLEWARE
    # Insert before MIDDLEWARE
    content = content.replace(
        "MIDDLEWARE = [",
        "AUTH_USER_MODEL = 'accounts.User'\n\nMIDDLEWARE = ["
    )
    print("[2/2] Added AUTH_USER_MODEL = 'accounts.User'")
else:
    print("[2/2] AUTH_USER_MODEL already set")

with open(SETTINGS, "w") as f:
    f.write(content)

print()
print("=" * 65)
print("  FIXES APPLIED")
print("=" * 65)
print()
print("  Now run:")
print("    cd /home/abia/abia-migration-observatory/abia-app")
print("    python manage.py migrate")
print()
