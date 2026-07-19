#!/usr/bin/env python3
"""
Fix: Add LOGIN_URL to settings.py so @login_required redirects work.
"""

import os

SETTINGS = "/home/abia/abia-migration-observatory/abia-app/abia/settings.py"

with open(SETTINGS, "r") as f:
    content = f.read()

# Check if LOGIN_URL already exists
if "LOGIN_URL" in content:
    print("LOGIN_URL already configured")
    exit(0)

# Add LOGIN_URL before the last line or after CELERY settings
if "CELERY_RESULT_BACKEND" in content:
    content = content.replace(
        "CELERY_RESULT_BACKEND",
        "LOGIN_URL = '/admin/login/'\n\nCELERY_RESULT_BACKEND"
    )
    print("Added LOGIN_URL = '/admin/login/'")
else:
    # Append at end
    content = content.rstrip() + "\n\nLOGIN_URL = '/admin/login/'\n"
    print("Added LOGIN_URL = '/admin/login/'")

with open(SETTINGS, "w") as f:
    f.write(content)

print("Done. Restart the server and try /dashboard/ again.")
