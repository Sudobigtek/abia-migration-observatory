#!/usr/bin/env python3
# NASA F-String Mass Repair v1.0
from pathlib import Path
import os

PROJECT_ROOT = Path.home() / "abia-migration-observatory" / "abia-app"

BROKEN_FILES = [
    "dynamic_fields_backup_47470/services.py",
    "dynamic_fields/common_exceptions_v2.py",
    "dynamic_fields/fix_tests_contract_compliant.py",
    "abia/common/kong_client.py",
    "abia/ncfrmi/services.py",
    "abia/migrants/odk_sync.py",
    "abia/iom/services.py",
    "abia/export_pipeline/views.py",
]

def fix_file(filepath):
    f = PROJECT_ROOT / filepath
    if not f.exists():
        print("SKIP (missing): " + filepath)
        return False
    lines = f.read_text(encoding="utf-8", errors="ignore").split("\n")
    fixed = []
    changed = False
    for i, line in enumerate(lines, 1):
        original = line
        stripped = line.lstrip()

        # Pattern A: f" containing inner " quotes -> convert to f'
        if stripped.startswith('f"') and '"' in stripped[2:]:
            line = line.replace('f"', "f'", 1)
            line = line.replace('\\"', '"')
            rstrip = line.rstrip()
            if rstrip.endswith('",'):
                line = rstrip[:-2] + "',"
            elif rstrip.endswith('"'):
                line = rstrip[:-1] + "'"
            if line != original:
                print("  [" + str(i) + '] Converted f" to f\' in ' + filepath)
                changed = True

        # Pattern B: f' containing \" escapes (invalid inside single quotes)
        elif stripped.startswith("f'") and '\\"' in line:
            line = line.replace('\\"', '"')
            rstrip = line.rstrip()
            if rstrip.endswith('",'):
                line = rstrip[:-2] + "',"
            elif rstrip.endswith('"'):
                line = rstrip[:-1] + "'"
            if line != original:
                print("  [" + str(i) + "] Removed bad \\\" escapes in " + filepath)
                changed = True

        fixed.append(line)

    f.write_text("\n".join(fixed), encoding="utf-8")
    return changed

def verify_syntax(filepath):
    f = PROJECT_ROOT / filepath
    if not f.exists():
        return True
    try:
        with open(str(f), "r", encoding="utf-8", errors="ignore") as src:
            compile(src.read(), str(f), "exec")
        return True
    except SyntaxError as e:
        print("  STILL BROKEN: " + filepath + " at line " + str(e.lineno) + ": " + str(e.msg))
        return False

print("=" * 60)
print("NASA F-STRING MASS REPAIR v1.0")
print("=" * 60)

total_fixed = 0
total_ok = 0
for fp in BROKEN_FILES:
    print("\nRepairing: " + fp)
    if fix_file(fp):
        total_fixed += 1
    if verify_syntax(fp):
        total_ok += 1
        print("  SYNTAX OK")
    else:
        print("  NEEDS MANUAL FIX")

print("\n" + "=" * 60)
print("RESULT: " + str(total_ok) + "/" + str(len(BROKEN_FILES)) + " files clean")
print("=" * 60)
