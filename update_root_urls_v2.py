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
        print("Already exists: " + path_str)
        continue

    # Split by lines using chr(10) to avoid literal backslash-n in the script
    lines = content.split(chr(10))
    new_lines = []
    inserted = False

    for line in lines:
        if not inserted and line.strip() == ']' and len(new_lines) > 0:
            indent = '    '
            new_lines.append(indent + 'path("' + path_str + '", include("' + module + '")),')
            inserted = True
        new_lines.append(line)

    content = chr(10).join(new_lines)
    print("Added: " + path_str)

with open(URLS_FILE, "w") as f:
    f.write(content)

print("Root urls.py updated successfully.")
