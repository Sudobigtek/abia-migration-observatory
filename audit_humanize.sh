#!/bin/bash
# ============================================
# NASA Diagnostic Script - Abia Migration Observatory
# Audit for missing {% load humanize %} across all templates
# ============================================

echo "========================================"
echo "AUDIT: Humanize Filter Usage in Templates"
echo "========================================"
echo ""

PROJECT_DIR="/home/abia/abia-migration-observatory/abia-app"
TEMPLATES_DIR="$PROJECT_DIR/templates"

# Find all templates using humanize filters
echo "[1] Scanning for humanize filter usage..."
echo "----------------------------------------"
HUMANIZE_FILES=$(grep -rlE '\|intcomma|\|intword|\|ordinal|\|naturaltime|\|naturalday' "$TEMPLATES_DIR" 2>/dev/null)

if [ -z "$HUMANIZE_FILES" ]; then
    echo "No humanize filters found in templates."
else
    echo "Files using humanize filters:"
    echo "$HUMANIZE_FILES" | while read -r file; do
        echo "  - $file"
    done
fi

echo ""
echo "[2] Checking for missing {% load humanize %}..."
echo "----------------------------------------"

ISSUES_FOUND=0
if [ -n "$HUMANIZE_FILES" ]; then
    echo "$HUMANIZE_FILES" | while read -r file; do
        if ! grep -q "{% load humanize %}" "$file"; then
            echo "  ⚠️  MISSING: $file"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        else
            echo "  ✅ OK: $file"
        fi
    done
fi

echo ""
echo "[3] Scanning all apps for templates with number formatting..."
echo "----------------------------------------"

# Also check app-level templates
for app_dir in "$PROJECT_DIR"/abia/*/; do
    if [ -d "$app_dir/templates" ]; then
        APP_ISSUES=$(grep -rlE '\|intcomma|\|intword|\|ordinal|\|naturaltime|\|naturalday' "$app_dir/templates" 2>/dev/null)
        if [ -n "$APP_ISSUES" ]; then
            echo "App: $(basename "$app_dir")"
            echo "$APP_ISSUES" | while read -r file; do
                if ! grep -q "{% load humanize %}" "$file"; then
                    echo "  ⚠️  MISSING: $file"
                else
                    echo "  ✅ OK: $file"
                fi
            done
        fi
    fi
done

echo ""
echo "[4] Verifying INSTALLED_APPS contains humanize..."
echo "----------------------------------------"
if grep -q "'django.contrib.humanize'" "$PROJECT_DIR/abia/settings.py"; then
    echo "  ✅ django.contrib.humanize is in INSTALLED_APPS"
else
    echo "  ❌ django.contrib.humanize is MISSING from INSTALLED_APPS"
fi

echo ""
echo "========================================"
echo "AUDIT COMPLETE"
echo "========================================"
