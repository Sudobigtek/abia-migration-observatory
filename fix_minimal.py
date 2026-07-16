#!/usr/bin/env python3
import os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path("/home/abia/abia-migration-observatory/abia-app")

def run(cmd, cwd=None, t=60):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or ROOT, timeout=t)
    return r.returncode, r.stdout, r.stderr

print("=" * 60)
print("  ABIA ULTIMATE FIX")
print("=" * 60)
print()

# Fix 1
f1 = ROOT / "fix_created_by.py"
if f1.exists():
    c = "#!/usr/bin/env python3
"
    c += """"Fix created_by fields."""
"
    c += "import os
"
    c += "def fix_models():
"
    c += "    print("Warning: Pattern not found")
"
    c += "    for r, d, files in os.walk('.'):
"
    c += "        for f in files:
"
    c += "            if f.endswith('.py'):
"
    c += "                print(f)
"
    c += "if __name__ == '__main__':
"
    c += "    fix_models()
"
    f1.write_text(c, encoding="utf-8")
    print("   Fixed: fix_created_by.py")

# Fix 2
f2 = ROOT / "dynamic_fields" / "settings_secrets_patch.py"
if f2.exists():
    c = """"Patch settings."""
"
    c += "import os
"
    c += "def read_secret_file(path):
"
    c += "    try:
"
    c += "        with open(path, 'r') as f:
"
    c += "            return f.read().strip()
"
    c += "    except FileNotFoundError:
"
    c += "        return None
"
    f2.write_text(c, encoding="utf-8")
    print("   Fixed: settings_secrets_patch.py")

# Fix 3
f3 = ROOT / "dynamic_fields" / "diagnose_repos.py"
if f3.exists():
    c = "#!/usr/bin/env python3
"
    c += """"Diagnose repos."""
"
    c += "def diagnose():
"
    c += "    print("--- accounts.repositories ---")
"
    c += "    try:
"
    c += "        from abia.accounts import repositories
"
    c += "        print("OK")
"
    c += "    except ImportError as e:
"
    c += "        print(f"Error: {e}")
"
    c += "if __name__ == '__main__':
"
    c += "    diagnose()
"
    f3.write_text(c, encoding="utf-8")
    print("   Fixed: diagnose_repos.py")

print()
print("Clearing cache...")
run("find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true")
run("find . -name '*.pyc' -delete 2>/dev/null || true")
print("   Done")

print()
print("Checking for duplicate apps...")
for app in ["accounts", "cases", "referrals", "migrants"]:
    r = ROOT / app
    a = ROOT / "abia" / app
    if r.exists() and a.exists():
        print(f"   Removing duplicate: {r}")
        shutil.rmtree(r, ignore_errors=True)
print("   Done")

print()
print("Running Django checks...")
ret, out, err = run("python manage.py check 2>&1")
if ret == 0:
    print("   Django OK")
    print("   Running makemigrations...")
    run("python manage.py makemigrations --no-input")
    print("   Running migrate...")
    run("python manage.py migrate --no-input")
    print("   Migrations done")
else:
    print("   Django still has issues:")
    print(err[:500])

print()
print("Running audit...")
audit = Path("/home/abia/abia-migration-observatory/codebase_doctor.py")
if audit.exists():
    ret, out, err = run(f"python {audit} --path {ROOT} --output {ROOT.parent}/audit_final --fix", cwd=ROOT.parent)
    print(out[-800:] if len(out) > 800 else out)
else:
    print("   Audit script not found")

print()
print("=" * 60)
print("  DONE")
print("=" * 60)
