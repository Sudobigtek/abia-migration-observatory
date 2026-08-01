#!/usr/bin/env python3
"""Surgical template URL repair — v2."""
from pathlib import Path

PROJECT_ROOT = Path.home() / "abia-migration-observatory" / "abia-app"
TPL_DIR = PROJECT_ROOT / "templates"

fixes = 0
for f in TPL_DIR.rglob("*.html"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    original = text

    # Fix bare public_dashboard
    text = text.replace("{% url 'public_dashboard' %}", "{% url 'public_dashboard:dashboard' %}")
    text = text.replace('{% url "public_dashboard" %}', "{% url 'public_dashboard:dashboard' %}")

    # Fix wrong namespaced public_dashboard:public_dashboard
    text = text.replace("{% url 'public_dashboard:public_dashboard' %}", "{% url 'public_dashboard:dashboard' %}")
    text = text.replace('{% url "public_dashboard:public_dashboard" %}', "{% url 'public_dashboard:dashboard' %}")

    # Fix wrong namespaced public_dashboard:public_feedback -> public_dashboard:feedback
    text = text.replace("{% url 'public_dashboard:public_feedback' %}", "{% url 'public_dashboard:feedback' %}")
    text = text.replace('{% url "public_dashboard:public_feedback" %}', "{% url 'public_dashboard:feedback' %}")

    # Fix bare public_feedback -> public_dashboard:feedback
    text = text.replace("{% url 'public_feedback' %}", "{% url 'public_dashboard:feedback' %}")
    text = text.replace('{% url "public_feedback" %}', "{% url 'public_dashboard:feedback' %}")

    if text != original:
        f.write_text(text, encoding="utf-8")
        fixes += 1
        print("FIXED: " + str(f.relative_to(PROJECT_ROOT)))

if fixes == 0:
    print("No broken template URLs found.")
else:
    print("\nFixed " + str(fixes) + " template file(s).")
