#!/usr/bin/env python3
"""
ABIA Migration Observatory — Complete Fix Script
Handles: Unicode curly quotes, duplicate Django apps, migration issues
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path("/home/abia/abia-migration-observatory/abia-app")

# Mapping of curly quotes to straight quotes
CURLY_TO_STRAIGHT = {
    '\u201c': '"',   # Left double quotation mark
    '\u201d': '"',   # Right double quotation mark
    '\u2018': "'",   # Left single quotation mark
    '\u2019': "'",   # Right single quotation mark
    '\u201a': ",",   # Single low-9 quotation mark
    '\u201e': '"',   # Double low-9 quotation mark
    '\u201f': '"',   # Double high-reversed-9 quotation mark
}

def fix_curly_quotes(filepath):
    """Replace all curly quotes with straight quotes in a file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        for curly, straight in CURLY_TO_STRAIGHT.items():
            content = content.replace(curly, straight)
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"   ❌ Error fixing {filepath}: {e}")
        return False

def find_duplicate_apps():
    """Find all Django apps that exist in both root and abia/ subfolder."""
    duplicates = []
    app_names = ['accounts', 'cases', 'referrals', 'migrants']

    for app in app_names:
        root_app = PROJECT_ROOT / app
        abia_app = PROJECT_ROOT / 'abia' / app

        if root_app.exists() and abia_app.exists():
            duplicates.append({
                'name': app,
                'root_path': root_app,
                'abia_path': abia_app
            })

    return duplicates

def check_urls_reference(app_name):
    """Check which version of an app is referenced in urls.py."""
    urls_file = PROJECT_ROOT / 'abia' / 'urls.py'
    if not urls_file.exists():
        return None

    content = urls_file.read_text(encoding='utf-8')

    # Check for 'abia.{app}' pattern
    if f"abia.{app_name}" in content:
        return 'abia'
    # Check for just '{app}' pattern (but not as part of abia.{app})
    if re.search(rf'["\']{app_name}["\']', content):
        return 'root'

    return None

def main():
    print("🔧 STEP 1: Fixing curly quotes in all Python files...")

    fixed_files = []
    broken_files = [
        PROJECT_ROOT / 'fix_created_by.py',
        PROJECT_ROOT / 'dynamic_fields' / 'settings_secrets_patch.py',
        PROJECT_ROOT / 'dynamic_fields' / 'diagnose_repos.py',
    ]

    # Also scan all Python files for curly quotes
    for py_file in PROJECT_ROOT.rglob('*.py'):
        if fix_curly_quotes(py_file):
            fixed_files.append(str(py_file.relative_to(PROJECT_ROOT)))

    if fixed_files:
        print(f"   ✅ Fixed curly quotes in {len(fixed_files)} files:")
        for f in fixed_files[:10]:
            print(f"      • {f}")
        if len(fixed_files) > 10:
            print(f"      ... and {len(fixed_files) - 10} more")
    else:
        print("   ⚠️  No curly quotes found (may already be fixed)")

    print("")
    print("🔧 STEP 2: Detecting duplicate Django apps...")

    duplicates = find_duplicate_apps()

    if not duplicates:
        print("   ✅ No duplicate apps found.")
    else:
        print(f"   Found {len(duplicates)} duplicate app(s):")
        for dup in duplicates:
            print(f"      • {dup['name']}: {dup['root_path']} vs {dup['abia_path']}")

        print("")
        print("   Checking urls.py references...")

        for dup in duplicates:
            ref = check_urls_reference(dup['name'])
            if ref == 'abia':
                print(f"   urls.py uses 'abia.{dup['name']}' → keeping abia/{dup['name']}/")
                print(f"   🗑️  Removing: {dup['root_path']}")
                shutil.rmtree(dup['root_path'])
                print(f"   ✅ Removed.")
            elif ref == 'root':
                print(f"   urls.py uses '{dup['name']}' → keeping {dup['name']}/")
                print(f"   🗑️  Removing: {dup['abia_path']}")
                shutil.rmtree(dup['abia_path'])
                print(f"   ✅ Removed.")
            else:
                print(f"   ⚠️  Cannot determine reference for '{dup['name']}' in urls.py")
                print(f"      Defaulting to keep abia/{dup['name']}/")
                print(f"   🗑️  Removing: {dup['root_path']}")
                shutil.rmtree(dup['root_path'])
                print(f"   ✅ Removed.")

    print("")
    print("🔧 STEP 3: Clearing Python cache files...")

    # Remove all __pycache__ and .pyc files to clear stale imports
    pycache_count = 0
    for pycache in PROJECT_ROOT.rglob('__pycache__'):
        shutil.rmtree(pycache)
        pycache_count += 1
    for pyc in PROJECT_ROOT.rglob('*.pyc'):
        pyc.unlink()
        pycache_count += 1

    print(f"   ✅ Cleared {pycache_count} cache files/directories")

    print("")
    print("🔧 STEP 4: Running Django checks...")

    os.chdir(PROJECT_ROOT)

    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'check'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("   ✅ Django checks passed!")
            print("")
            print("   Running makemigrations...")
            subprocess.run([sys.executable, 'manage.py', 'makemigrations', '--no-input'], timeout=60)
            print("   Running migrate...")
            subprocess.run([sys.executable, 'manage.py', 'migrate', '--no-input'], timeout=60)
            print("   ✅ Migrations complete!")
        else:
            print("   ❌ Django checks still failing:")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"   ❌ Error running Django commands: {e}")

    print("")
    print("═══════════════════════════════════════════════════════════════")
    print("  ✅ FIX SCRIPT COMPLETE")
    print("═══════════════════════════════════════════════════════════════")
    print("")
    print("Next steps:")
    print("   1. Run the audit again: cd /home/abia/abia-migration-observatory && ./run_audit.sh")
    print("   2. Or test Django: cd /home/abia/abia-migration-observatory/abia-app && python manage.py runserver")
    print("")

if __name__ == '__main__':
    main()
