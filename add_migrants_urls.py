#!/usr/bin/env python3
"""
ABIA Migration Observatory — Add migrants API to root urls.py
"""

import os

URLS_FILE = "/home/abia/abia-migration-observatory/abia-app/abia/urls.py"

if not os.path.exists(URLS_FILE):
    print("ERROR: " + URLS_FILE + " not found")
    exit(1)

with open(URLS_FILE, "r") as f:
    content = f.read()

# Check if already added
if 'abia.migrants.urls' in content:
    print("Migrants API URL already configured")
    exit(0)

# Add the import if missing
if 'from django.urls import path, include' not in content:
    if 'from django.urls import path' in content:
        content = content.replace(
            'from django.urls import path',
            'from django.urls import path, include'
        )
        print("Updated import to include 'include'")
    else:
        # Add import at top
        content = "from django.urls import path, include\n" + content
        print("Added 'from django.urls import path, include'")

# Add the migrants path before the closing bracket of urlpatterns
# Find the last line of urlpatterns and insert before it
lines = content.split('\n')
new_lines = []
inserted = False

for i, line in enumerate(lines):
    # Look for a line that ends urlpatterns (closing bracket)
    if not inserted and line.strip() == ']' and i > 0:
        # Insert before this line
        indent = len(line) - len(line.lstrip())
        new_lines.append(' ' * indent + '    path("api/v1/migrants/", include("abia.migrants.urls")),')
        inserted = True
    new_lines.append(line)

content = '\n'.join(new_lines)

with open(URLS_FILE, "w") as f:
    f.write(content)

print("Added: path('api/v1/migrants/', include('abia.migrants.urls'))")
print("Done.")
