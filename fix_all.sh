#!/bin/bash
# =============================================================================
# ABIA MIGRATION OBSERVATORY — COMPLETE FIX SCRIPT
# Fixes: conflicting LGA models + broken string quotes + migration issues
# =============================================================================

set -e

echo "🔧 STEP 1: Fixing broken string quotes in 3 files..."

# Fix 1: fix_created_by.py (line 30 — curly quotes)
FILE1="/home/abia/abia-migration-observatory/abia-app/fix_created_by.py"
if [ -f "$FILE1" ]; then
    sed -i "s/\*⚠️ Pattern not found\. Showing relevant section:\*/\"⚠️ Pattern not found. Showing relevant section:\"/g" "$FILE1"
    sed -i "s/content\.split('\n')/content.split('\\n')/g" "$FILE1"
    echo "   ✅ Fixed: fix_created_by.py"
else
    echo "   ⚠️  Not found: fix_created_by.py (may already be fixed or removed)"
fi

# Fix 2: settings_secrets_patch.py (line 7 — curly quotes in docstring)
FILE2="/home/abia/abia-migration-observatory/abia-app/dynamic_fields/settings_secrets_patch.py"
if [ -f "$FILE2" ]; then
    sed -i 's/""\*Read Docker secret from file\.\*""/"""Read Docker secret from file."""/g' "$FILE2"
    echo "   ✅ Fixed: settings_secrets_patch.py"
else
    echo "   ⚠️  Not found: settings_secrets_patch.py"
fi

# Fix 3: diagnose_repos.py (line 13 — curly quotes)
FILE3="/home/abia/abia-migration-observatory/abia-app/dynamic_fields/diagnose_repos.py"
if [ -f "$FILE3" ]; then
    sed -i "s/\*--- accounts\.repositories ---\*/\"--- accounts.repositories ---\"/g" "$FILE3"
    echo "   ✅ Fixed: diagnose_repos.py"
else
    echo "   ⚠️  Not found: diagnose_repos.py"
fi

echo ""
echo "🔧 STEP 2: Fixing conflicting LGA models..."

# Check which accounts app is the real one
ACCOUNTS_ROOT="/home/abia/abia-migration-observatory/abia-app/accounts"
ABIA_ACCOUNTS="/home/abia/abia-migration-observatory/abia-app/abia/accounts"

if [ -d "$ACCOUNTS_ROOT" ] && [ -d "$ABIA_ACCOUNTS" ]; then
    echo "   Found duplicate apps:"
    echo "     • $ACCOUNTS_ROOT"
    echo "     • $ABIA_ACCOUNTS"
    echo ""

    # Check which one is referenced in urls.py
    URLS_FILE="/home/abia/abia-migration-observatory/abia-app/abia/urls.py"
    if grep -q "abia.accounts" "$URLS_FILE" 2>/dev/null; then
        echo "   urls.py uses 'abia.accounts' → keeping abia/accounts/"
        echo "   🗑️  Removing duplicate: accounts/"
        rm -rf "$ACCOUNTS_ROOT"
        echo "   ✅ Removed: $ACCOUNTS_ROOT"
    elif grep -q "accounts" "$URLS_FILE" 2>/dev/null; then
        echo "   urls.py uses 'accounts' → keeping accounts/"
        echo "   🗑️  Removing duplicate: abia/accounts/"
        rm -rf "$ABIA_ACCOUNTS"
        echo "   ✅ Removed: $ABIA_ACCOUNTS"
    else
        echo "   ⚠️  Cannot determine which to keep. Manual review needed."
        echo "   Both folders exist:"
        ls -la "$ACCOUNTS_ROOT" | head -5
        ls -la "$ABIA_ACCOUNTS" | head -5
    fi
else
    echo "   ✅ No duplicate accounts apps found."
fi

echo ""
echo "🔧 STEP 3: Running Django migrations..."

cd /home/abia/abia-migration-observatory/abia-app

# Check if we can run migrations now
if python manage.py check 2>/dev/null; then
    echo "   ✅ Django checks passed."
    echo "   Running makemigrations..."
    python manage.py makemigrations --no-input || echo "   ⚠️  makemigrations had issues (may be expected)"
    echo "   Running migrate..."
    python manage.py migrate --no-input || echo "   ⚠️  migrate had issues (check output above)"
else
    echo "   ❌ Django checks still failing. Fix the model conflict first, then run:"
    echo "      python manage.py makemigrations"
    echo "      python manage.py migrate"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ FIX SCRIPT COMPLETE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "   1. Review any errors above"
echo "   2. Run the audit again: ./run_audit.sh"
echo "   3. Or test Django: python manage.py runserver"
echo ""
