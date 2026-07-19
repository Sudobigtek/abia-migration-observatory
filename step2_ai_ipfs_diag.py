#!/usr/bin/env python3
"""
Step 2: Diagnose AI and IPFS apps
"""

import os

APP_DIR = "/home/abia/abia-migration-observatory/abia-app/abia"

print("=" * 65)
print("  AI & IPFS APP DIAGNOSTIC")
print("=" * 65)

for app in ['ai', 'ipfs']:
    app_path = os.path.join(APP_DIR, app)
    print(f"\n--- abia.{app} ---")

    if not os.path.exists(app_path):
        print(f"  DIRECTORY MISSING: {app_path}")
        continue

    files = os.listdir(app_path)
    print(f"  Files: {files}")

    # Check for key files
    for key_file in ['models.py', 'views.py', 'urls.py', 'serializers.py', 'apps.py']:
        fpath = os.path.join(app_path, key_file)
        if os.path.exists(fpath):
            with open(fpath) as f:
                content = f.read()
            print(f"  {key_file}: {len(content)} chars")
            # Show first few lines
            for line in content.split(chr(10))[:5]:
                print(f"    {line}")
        else:
            print(f"  {key_file}: MISSING")

    # Check if app is in INSTALLED_APPS
    settings_path = os.path.join(APP_DIR, "settings.py")
    with open(settings_path) as f:
        settings = f.read()
    if f"'abia.{app}'" in settings or f'"abia.{app}"' in settings:
        print(f"  INSTALLED_APPS: YES")
    else:
        print(f"  INSTALLED_APPS: NO")
