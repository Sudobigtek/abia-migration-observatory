#!/usr/bin/env python3
"""Surgical fix for public_dashboard template URL references."""
from pathlib import Path

PROJECT_ROOT = Path.home() / "abia-migration-observatory" / "abia-app"
TPL_DIR = PROJECT_ROOT / "templates" / "public_dashboard"

fixes = 0
for f in TPL_DIR.rglob("*.html"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    original = text

    # Fix 1: bare 'public_dashboard' -> namespaced 'public_dashboard:dashboard'
    text = text.replace("{% url 'public_dashboard' %}", "{% url 'public_dashboard:dashboard' %}")

    # Fix 2: wrong namespaced 'public_dashboard:public_dashboard' -> 'public_dashboard:dashboard'
    text = text.replace("{% url 'public_dashboard:public_dashboard' %}", "{% url 'public_dashboard:dashboard' %}")

    # Fix 3: same fixes with double quotes (if any)
    text = text.replace('{% url "public_dashboard" %}', "{% url 'public_dashboard:dashboard' %}")
    text = text.replace('{% url "public_dashboard:public_dashboard" %}', "{% url 'public_dashboard:dashboard' %}")

    if text != original:
        f.write_text(text, encoding="utf-8")
        fixes += 1
        print("FIXED: " + str(f.relative_to(PROJECT_ROOT)))

if fixes == 0:
    print("No broken template URLs found.")
else:
    print("\nFixed " + str(fixes) + " template file(s).")
