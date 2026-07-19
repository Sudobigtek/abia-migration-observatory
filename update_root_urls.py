#!/usr/bin/env python3
"""
Add Cases, Referrals, and Accounts API routes to root urls.py
"""

import os

URLS_FILE = "/home/abia/abia-migration-observatory/abia-app/abia/urls.py"

if not os.path.exists(URLS_FILE):
    print("ERROR: " + URLS_FILE + " not found")
    exit(1)

with open(URLS_FILE, "r") as f:
    content = f.read()

routes = [
    ('abia.cases.urls', 'api/v1/cases/'),
    ('abia.referrals.urls', 'api/v1/referrals/'),
    ('abia.accounts.urls', 'api/v1/accounts/'),
]

for module, path_str in routes:
    if module in content:
        print(f"  Already exists: {path_str}")
        continue

    # Insert before the closing bracket of urlpatterns
    lines = content.split('
')
    new_lines = []
    inserted = False

    for line in lines:
        if not inserted and line.strip() == ']' and i > 0:
            indent = '    '
            new_lines.append(indent + 'path("' + path_str + '", include("' + module + '")),')
            inserted = True
        new_lines.append(line)

    content = '
'.join(new_lines)
    print(f"  Added: {path_str}")

with open(URLS_FILE, "w") as f:
    f.write(content)

print("Root urls.py updated successfully.")
