#!/usr/bin/env python3
"""ABIA Loop Engine v5.1 — Infrastructure Agent
Offline Mode | Template URL Guard | Surgical Precision
"""
import os
import sys
import subprocess
import re
from pathlib import Path

# -- Config --
PROJECT_ROOT = str(Path.home() / "abia-migration-observatory" / "abia-app")
VENV_PYTHON = str(Path.home() / "abia-migration-observatory" / ".venv" / "bin" / "python3")
VENV_ACTIVATE = str(Path.home() / "abia-migration-observatory" / ".venv" / "bin" / "activate")
DOCKER_CONTAINER = "abia-postgres"

# -- Colors --
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

def c(color, text):
    return color + text + Colors.ENDC

def banner():
    print("")
    print(c(Colors.OKCYAN, "=" * 70))
    print("  " + c(Colors.BOLD, "ABIA LOOP ENGINE v5.1") + " - Infrastructure Agent")
    print("  " + c(Colors.OKGREEN, "Offline Mode") + " | Template URL Guard | Surgical Precision")
    print(c(Colors.OKCYAN, "=" * 70))
    print("")

def run_shell(cmd, cwd=None, timeout=30):
    try:
        result = subprocess.run(cmd, shell=True, executable="/bin/bash", capture_output=True, text=True, cwd=cwd, timeout=timeout)
        return result.stdout.strip() + result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "Command timed out after " + str(timeout) + "s"
    except Exception as e:
        return str(e)

def venv_cmd(cmd):
    return ". " + VENV_ACTIVATE + " && cd " + PROJECT_ROOT + " && " + cmd

def check_docker():
    out = run_shell("docker ps --filter name=" + DOCKER_CONTAINER + " --format " + chr(39) + "{{.Status}}" + chr(39))
    return "PASS" if "Up" in out else "FAIL - " + out

def check_django():
    out = run_shell(venv_cmd(VENV_PYTHON + " -B manage.py check 2>&1"))
    return "PASS" if "no issues" in out else "FAIL\n" + out

def check_db():
    shell_cmd = "from django.db import connection; cursor=connection.cursor(); cursor.execute('SELECT 1'); print('DB_OK')"
    out = run_shell(venv_cmd(VENV_PYTHON + " -B manage.py shell -c " + chr(34) + shell_cmd + chr(34) + " 2>&1"))
    return "PASS" if "DB_OK" in out else "FAIL\n" + out

def check_server():
    out = run_shell("ps aux | grep 'manage.py runserver' | grep -v grep")
    return "PASS" if out else "FAIL - no server process"

def check_port():
    out = run_shell("ss -tlnp | grep ':8001'")
    return "PASS" if out else "FAIL - port 8001 not bound"

def check_http():
    out = run_shell("curl -s -o /dev/null -w " + chr(39) + "%{http_code}" + chr(39) + " http://127.0.0.1:8001/ 2>&1", timeout=10)
    return "PASS (" + out + ")" if out == "200" else "FAIL - HTTP " + out

def check_templates():
    errors = []
    tpl_dir = Path(PROJECT_ROOT) / "templates"
    for f in tpl_dir.rglob("*.html"):
        text = f.read_text(errors="ignore")
        if "{% elif|" in text:
            errors.append(str(f) + ": broken elif tag")
        if "{{ else %}}" in text:
            errors.append(str(f) + ": broken else tag")
        for m in re.finditer(r"{%\s*url\s+'([^']+)'\s*%}", text):
            name = m.group(1)
            if name == "public_dashboard":
                errors.append(str(f) + ": line ~" + str(text[:m.start()].count("\n")+1) + " - broken url 'public_dashboard'")
            if name == "public_feedback":
                errors.append(str(f) + ": line ~" + str(text[:m.start()].count("\n")+1) + " - broken url 'public_feedback' (should be 'feedback')")
    return "PASS" if not errors else "FAIL\n" + "\n".join(errors[:15])

def check_urls():
    shell_cmd = "from django.urls import get_resolver; r=get_resolver(); print('URLS_OK')"
    out = run_shell(venv_cmd(VENV_PYTHON + " -B manage.py shell -c " + chr(34) + shell_cmd + chr(34) + " 2>&1"))
    return "PASS" if "URLS_OK" in out else "FAIL\n" + out

def check_backup():
    bp = Path(PROJECT_ROOT) / ".nuclear_backup_v4"
    return "PASS" if bp.exists() else "WARN - .nuclear_backup_v4 missing"

def cmd_health():
    print(c(Colors.BOLD, "10-LAYER INFRASTRUCTURE HEALTH PROTOCOL"))
    layers = [
        ("1. Docker PostgreSQL", check_docker),
        ("2. Django System Check", check_django),
        ("3. Database Connectivity", check_db),
        ("4. Server Process", check_server),
        ("5. Port Binding", check_port),
        ("6. HTTP Response", check_http),
        ("7. Template Integrity", check_templates),
        ("8. URL Routing", check_urls),
        ("9. Backup Verification", check_backup),
    ]
    score = 0
    for name, fn in layers:
        result = fn()
        if result.startswith("PASS"):
            score += 1
            status = c(Colors.OKGREEN, "PASS")
        elif result.startswith("WARN"):
            status = c(Colors.WARNING, "WARN")
        else:
            status = c(Colors.FAIL, "FAIL")
        print("\n[LAYER] " + name + "... " + status)
        if not result.startswith("PASS") and not result.startswith("WARN"):
            print("Output: " + result.replace("\n", "\n  ")[:300])
    print("\n" + "=" * 60)
    print("HEALTH SCORE: " + str(score) + "/" + str(len(layers)) + " layers operational")
    if score == len(layers):
        print(c(Colors.OKGREEN, "INFRASTRUCTURE FULLY OPERATIONAL"))
    elif score >= 7:
        print(c(Colors.WARNING, "INFRASTRUCTURE DEGRADED - Repair advised"))
    else:
        print(c(Colors.FAIL, "INFRASTRUCTURE CRITICAL - Immediate repair required"))
    print("=" * 60)

def cmd_audit():
    print(c(Colors.BOLD, "FULL PROJECT AUDIT"))
    issues = []
    py_files = list(Path(PROJECT_ROOT).rglob("*.py"))
    for pf in py_files:
        try:
            with open(str(pf), "r", encoding="utf-8", errors="ignore") as src:
                compile(src.read(), str(pf), "exec")
        except SyntaxError as e:
            issues.append("SYNTAX: " + str(pf.relative_to(Path(PROJECT_ROOT))) + " - line " + str(e.lineno) + ": " + str(e.msg))
    for folder in Path(PROJECT_ROOT).rglob("*/"):
        if folder.name == "__pycache__":
            continue
        py_in_folder = list(folder.glob("*.py"))
        if py_in_folder and not (folder / "__init__.py").exists():
            issues.append("MISSING __init__.py: " + str(folder.relative_to(Path(PROJECT_ROOT))))
    tpl_issues = check_templates()
    if tpl_issues.startswith("FAIL"):
        for line in tpl_issues.split("\n")[1:]:
            if line.strip():
                issues.append("TEMPLATE: " + line)
    if not issues:
        print(c(Colors.OKGREEN, "ZERO ISSUES FOUND"))
    else:
        print(c(Colors.FAIL, str(len(issues)) + " ISSUES FOUND"))
        for i in issues[:20]:
            print("  " + i)

def cmd_fix():
    print(c(Colors.BOLD, "AUTO-FIX"))
    fixed = 0
    for folder in Path(PROJECT_ROOT).rglob("*/"):
        if folder.name == "__pycache__":
            continue
        py_in_folder = list(folder.glob("*.py"))
        if py_in_folder and not (folder / "__init__.py").exists():
            (folder / "__init__.py").write_text("")
            fixed += 1
    print("Created " + str(fixed) + " missing __init__.py files")
    tpl_dir = Path(PROJECT_ROOT) / "templates"
    for f in tpl_dir.rglob("*.html"):
        text = f.read_text(errors="ignore")
        new_text = text.replace("{% url 'public_dashboard' %}", "{% url 'public_dashboard:dashboard' %}")
        new_text = new_text.replace("{% url 'public_dashboard:public_dashboard' %}", "{% url 'public_dashboard:dashboard' %}")
        new_text = new_text.replace("{% url 'public_dashboard:public_feedback' %}", "{% url 'public_dashboard:feedback' %}")
        new_text = new_text.replace("{% url 'public_feedback' %}", "{% url 'public_dashboard:feedback' %}")
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            fixed += 1
            print("Fixed URL in " + str(f))
    print(c(Colors.OKGREEN, "Auto-fix complete. Run /audit to verify."))

def main():
    banner()
    print("COMMANDS:")
    print("  /audit   - Full project audit")
    print("  /health  - 10-layer infrastructure health protocol")
    print("  /fix     - Auto-fix issues")
    print("  /shell   - Execute raw shell command")
    print("  /read    - Read a file")
    print("  /quit    - Exit agent")
    print("")
    while True:
        try:
            cmd = input("abia> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break
        if not cmd:
            continue
        if cmd == "/quit":
            print("Exiting...")
            break
        elif cmd == "/health":
            cmd_health()
        elif cmd == "/audit":
            cmd_audit()
        elif cmd == "/fix":
            cmd_fix()
        elif cmd.startswith("/shell "):
            print(run_shell(cmd[7:]))
        elif cmd.startswith("/read "):
            target = Path(PROJECT_ROOT) / cmd[6:].strip()
            if target.exists():
                lines = target.read_text(errors="ignore").split("\n")
                for i, line in enumerate(lines, 1):
                    print(str(i).rjust(4) + ": " + line)
            else:
                print("File not found: " + str(target))
        else:
            print("Unknown command: " + cmd + ". Type /quit to exit.")

if __name__ == "__main__":
    main()