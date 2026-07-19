#!/usr/bin/env python3
"""
Emergency repair of corrupted settings.py
"""

import os
import re

SETTINGS = "/home/abia/abia-migration-observatory/abia-app/abia/settings.py"

with open(SETTINGS, "r") as f:
    content = f.read()

# Find the corrupted CELERY_RESULT_BACKEND line and fix it
# Pattern: CELERY_RESULT_BACKEND = os.environ.get('...something broken...
# We need to replace the entire broken line with the correct one

lines = content.split(chr(10))
new_lines = []
fixed = False

for line in lines:
    # Detect corrupted CELERY line
    if "CELERY_RESULT_BACKEND = os.environ.get('LOGIN_URL" in line:
        new_lines.append("CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')")
        fixed = True
        continue

    # Also catch partial corruption
    if "os.environ.get('LOGIN_URL" in line and "CELERY" in line:
        new_lines.append("CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')")
        fixed = True
        continue

    new_lines.append(line)

# Remove any standalone LOGIN_URL that might have been added broken
final_lines = []
for line in new_lines:
    if line.strip().startswith("LOGIN_URL = '/admin/login/'") and "=" in line and line.count("'") < 2:
        continue  # Skip broken LOGIN_URL lines
    final_lines.append(line)

content = chr(10).join(final_lines)

# Add proper LOGIN_URL at the end if not present
if "LOGIN_URL = '/admin/login/'" not in content:
    content = content.rstrip() + chr(10) + chr(10) + "LOGIN_URL = '/admin/login/'" + chr(10)

with open(SETTINGS, "w") as f:
    f.write(content)

print("Settings.py repaired. Fixed CELERY line: " + str(fixed))
