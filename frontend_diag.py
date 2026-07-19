#!/usr/bin/env python3
"""
ABIA Migration Observatory — Frontend Diagnostic
Checks existing templates, static files, and frontend structure.
"""

import os

APP_DIR = "/home/abia/abia-migration-observatory/abia-app"

# Check templates directory
print("=" * 70)
print("  FRONTEND DIAGNOSTIC REPORT")
print("=" * 70)

# Check for templates
templates_dir = os.path.join(APP_DIR, "templates")
print("\n--- TEMPLATES ---")
if os.path.exists(templates_dir):
    for root, dirs, files in os.walk(templates_dir):
        level = root.replace(templates_dir, '').count(os.sep)
        indent = '  ' * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = '  ' * (level + 1)
        for f in sorted(files):
            print(f'{subindent}{f}')
else:
    print("  [NO TEMPLATES DIRECTORY]")

# Check for static files
static_dir = os.path.join(APP_DIR, "static")
print("\n--- STATIC FILES ---")
if os.path.exists(static_dir):
    for root, dirs, files in os.walk(static_dir):
        level = root.replace(static_dir, '').count(os.sep)
        if level > 1:
            continue
        indent = '  ' * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = '  ' * (level + 1)
        for f in sorted(files)[:20]:
            print(f'{subindent}{f}')
        if len(files) > 20:
            print(f'{subindent}... and {len(files)-20} more')
else:
    print("  [NO STATIC DIRECTORY]")

# Check for existing frontend-templates (from git status)
frontend_templates_dir = os.path.join(APP_DIR, "frontend-templates")
print("\n--- FRONTEND-TEMPLATES ---")
if os.path.exists(frontend_templates_dir):
    for root, dirs, files in os.walk(frontend_templates_dir):
        level = root.replace(frontend_templates_dir, '').count(os.sep)
        indent = '  ' * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = '  ' * (level + 1)
        for f in sorted(files):
            print(f'{subindent}{f}')
else:
    print("  [NO FRONTEND-TEMPLATES DIRECTORY]")

# Check base template
base_template = os.path.join(templates_dir, "base.html")
print("\n--- BASE TEMPLATE ---")
if os.path.exists(base_template):
    with open(base_template) as f:
        content = f.read()
    print(f"  EXISTS: {len(content)} chars")
    # Show key blocks
    for line in content.split(chr(10))[:30]:
        print(f"    {line}")
else:
    print("  [NO BASE.HTML]")

# Check landing page
landing_template = os.path.join(templates_dir, "landing.html")
print("\n--- LANDING PAGE ---")
if os.path.exists(landing_template):
    with open(landing_template) as f:
        content = f.read()
    print(f"  EXISTS: {len(content)} chars")
    for line in content.split(chr(10))[:20]:
        print(f"    {line}")
else:
    print("  [NO LANDING.HTML]")
