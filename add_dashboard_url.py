#!/usr/bin/env python3
"""
Add dashboard route to root urls.py
"""

import os

URLS_FILE = "/home/abia/abia-migration-observatory/abia-app/abia/urls.py"
VIEWS_FILE = "/home/abia/abia-migration-observatory/abia-app/abia/views.py"

# Create views.py
views_content = """from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, "dashboard.html")
"""

if not os.path.exists(VIEWS_FILE):
    with open(VIEWS_FILE, "w") as f:
        f.write(views_content)
    print("Created abia/views.py")

# Update urls.py
with open(URLS_FILE, "r") as f:
    content = f.read()

if "from abia import views" not in content:
    content = "from abia import views\n" + content
    print("Added import")

if 'path("dashboard/"' not in content:
    lines = content.split(chr(10))
    new_lines = []
    inserted = False
    for line in lines:
        if not inserted and line.strip() == ']' and len(new_lines) > 0:
            new_lines.append('    path("dashboard/", views.dashboard, name="dashboard"),')
            inserted = True
        new_lines.append(line)
    content = chr(10).join(new_lines)
    print("Added dashboard URL")
else:
    print("Dashboard URL already exists")

with open(URLS_FILE, "w") as f:
    f.write(content)

print("Done.")
