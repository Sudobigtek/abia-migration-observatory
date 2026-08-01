#!/usr/bin/env python3
# NASA Deep Scan v1.0 — Finds what's hiding
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "abia-migration-observatory" / "abia-app"
VENV = Path.home() / "abia-migration-observatory" / ".venv" / "bin" / "python3"

def run(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, executable="/bin/bash")
    return r.stdout.strip() + r.stderr.strip()

def section(title):
    print("\n" + "=" * 70)
    print("  " + title)
    print("=" * 70)

section("1. DOCKER CONTAINERS")
print(run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"))

section("2. CELERY TASK DISCOVERY")
out = run("cd " + str(ROOT) + " && source ../.venv/bin/activate && celery -A abia inspect registered 2>&1 | head -30")
if "Error" in out or "ImportError" in out:
    print("FAIL — " + out[:300])
else:
    print("PASS — Tasks discovered")
    print(out[:500])

section("3. OLLAMA CONNECTIVITY")
out = run("curl -s http://localhost:11434/api/tags 2>&1 | head -1")
if "llama" in out.lower():
    print("PASS — Ollama responding with models")
else:
    print("FAIL — " + out[:200])

section("4. DJANGO → OLLAMA (from app container)")
out = run("docker exec abia-django python3 -c \"import urllib.request; print(urllib.request.urlopen('http://ollama:11434/api/tags', timeout=5).read().decode()[:100])\" 2>&1")
if "llama" in out.lower():
    print("PASS — Django container can reach Ollama")
else:
    print("WARN — Django container cannot reach Ollama: " + out[:200])

section("5. IPFS CONNECTIVITY")
out = run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5001/api/v0/id 2>&1")
if out == "200":
    print("PASS — IPFS daemon responding")
else:
    print("WARN — IPFS not reachable (HTTP " + out + ")")

section("6. KONG GATEWAY")
out = run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8001/status 2>&1")
if out == "200":
    print("PASS — Kong Admin API responding")
else:
    print("WARN — Kong not reachable (HTTP " + out + ")")

section("7. MISSING __init__.py")
missing = []
for folder in ROOT.rglob("*/"):
    if folder.name == "__pycache__":
        continue
    py_files = list(folder.glob("*.py"))
    if py_files and not (folder / "__init__.py").exists():
        missing.append(str(folder.relative_to(ROOT)))
if missing:
    print("WARN — " + str(len(missing)) + " folders missing __init__.py")
    for m in missing[:10]:
        print("  " + m)
else:
    print("PASS — All Python packages have __init__.py")

section("8. BROKEN TEMPLATE URLS (all .html files)")
errors = []
for f in (ROOT / "templates").rglob("*.html"):
    text = f.read_text(errors="ignore")
    for line in text.split("\n"):
        if "{% url" in line:
            # Check for common broken patterns
            if "public_dashboard" in line and "public_dashboard:" not in line and "public_dashboard'" in line:
                if "public_dashboard:dashboard" not in line and "public_dashboard:feedback" not in line:
                    errors.append(str(f.relative_to(ROOT)) + ": " + line.strip()[:80])
if errors:
    print("WARN — " + str(len(errors)) + " potential broken URL tags")
    for e in errors[:10]:
        print("  " + e)
else:
    print("PASS — No obvious broken URL tags")

section("9. DATABASE TABLES & MIGRATIONS")
out = run("cd " + str(ROOT) + " && source ../.venv/bin/activate && python3 -B manage.py showmigrations 2>&1 | grep -c '\\[X\\]'")
applied = out.strip()
out2 = run("cd " + str(ROOT) + " && source ../.venv/bin/activate && python3 -B manage.py shell -c \"from django.db import connection; cursor=connection.cursor(); cursor.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'\"); print(cursor.fetchone()[0])\" 2>&1")
print("Applied migrations: " + applied)
print("Database tables: " + out2[:50])

section("10. STATIC FILES")
out = run("cd " + str(ROOT) + " && source ../.venv/bin/activate && python3 -B manage.py collectstatic --noinput --dry-run 2>&1 | tail -5")
if "static files" in out.lower():
    print("INFO — " + out)
else:
    print("PASS — Static files collected")

section("11. DJANGO SUPERUSER")
out = run("cd " + str(ROOT) + " && source ../.venv/bin/activate && python3 -B manage.py shell -c \"from django.contrib.auth import get_user_model; print('USERS:', get_user_model().objects.count())\" 2>&1")
print(out)

section("12. SECURITY POSTURE")
out = run("cd " + str(ROOT) + " && source ../.venv/bin/activate && python3 -B manage.py shell -c \"from django.conf import settings; print('DEBUG:', settings.DEBUG); print('SECRET_KEY_LENGTH:', len(settings.SECRET_KEY)); print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS[:3])\" 2>&1")
print(out)

section("13. GITHUB STATUS")
out = run("cd ~/abia-migration-observatory && git status --short | head -10")
if out:
    print("UNCOMMITTED CHANGES:")
    print(out)
else:
    print("PASS — Working tree clean")

section("14. SYNTAX ERRORS (all .py files)")
broken = []
for pf in ROOT.rglob("*.py"):
    try:
        with open(str(pf), "r", encoding="utf-8", errors="ignore") as src:
            compile(src.read(), str(pf), "exec")
    except SyntaxError as e:
        broken.append(str(pf.relative_to(ROOT)) + " line " + str(e.lineno))
if broken:
    print("FAIL — " + str(len(broken)) + " files with syntax errors")
    for b in broken[:10]:
        print("  " + b)
else:
    print("PASS — Zero syntax errors across all " + str(len(list(ROOT.rglob('*.py')))) + " Python files")

section("15. ENDPOINT HEALTH")
endpoints = [
    ("http://127.0.0.1:8001/", "Landing"),
    ("http://127.0.0.1:8001/public-dashboard/feedback/", "Feedback"),
    ("http://127.0.0.1:8001/public-dashboard/register/", "Register"),
    ("http://127.0.0.1:8001/admin/", "Admin"),
]
for url, name in endpoints:
    code = run("curl -s -o /dev/null -w '%{http_code}' " + url + " 2>&1")
    status = "PASS" if code in ["200", "302"] else "FAIL"
    print("  " + status + " " + code + " " + name + " (" + url + ")")

section("SCAN COMPLETE")
print("Review WARN and FAIL items above.")
print("=" * 70)
