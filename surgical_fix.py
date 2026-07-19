#!/usr/bin/env python3
"""
Surgical fix: Delete the orphan line 119 from settings.py
"""

SETTINGS = "/home/abia/abia-migration-observatory/abia-app/abia/settings.py"

with open(SETTINGS, "r") as f:
    lines = f.readlines()

# Find and remove the orphan line
new_lines = []
removed = False

for i, line in enumerate(lines, start=1):
    if i == 119 and "CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')" in line:
        print(f"Removed orphan line {i}: {line.strip()}")
        removed = True
        continue
    new_lines.append(line)

with open(SETTINGS, "w") as f:
    f.writelines(new_lines)

print("Settings.py fixed. Removed orphan line." if removed else "No orphan line found.")
