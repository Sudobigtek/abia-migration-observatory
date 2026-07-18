#!/usr/bin/env python3
import os

URLS_FILE = "/home/abia/abia-migration-observatory/abia-app/abia/urls.py"

if not os.path.exists(URLS_FILE):
    print("ERROR: " + URLS_FILE + " not found")
    exit(1)

with open(URLS_FILE, 'r') as f:
    content = f.read()

if "from django.views.generic import TemplateView" not in content:
    content = "from django.views.generic import TemplateView
" + content
    print("Added TemplateView import")

landing_path = "    path('', TemplateView.as_view(template_name='landing.html'), name='home'),"
if "path('', TemplateView.as_view(template_name='landing.html')" not in content:
    content = content.replace(
        "urlpatterns = [",
        "urlpatterns = [
" + landing_path
    )
    print("Added landing page route")
else:
    print("Landing page route already exists")

with open(URLS_FILE, 'w') as f:
    f.write(content)

print("urls.py updated successfully")
