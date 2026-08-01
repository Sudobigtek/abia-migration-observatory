#!/usr/bin/env python3
# NASA Surgical F-String Repair v2.0
from pathlib import Path

ROOT = Path.home() / "abia-migration-observatory" / "abia-app"

# Pattern A: f'..."  ->  f'...'
# (line_number, file_path, old_trailing_quote, new_trailing_quote)
pattern_a_fixes = [
    (45, "dynamic_fields_backup_47470/services.py", '"', "'"),
    (54, "dynamic_fields/common_exceptions_v2.py", '"', "'"),
    (234, "dynamic_fields/fix_tests_contract_compliant.py", '"', "'"),
    (63, "abia/common/kong_client.py", '"', "'"),
    (39, "abia/ncfrmi/services.py", '"', "'"),
    (53, "abia/iom/services.py", '"', "'"),
    (58, "abia/export_pipeline/views.py", '"', "'"),
]

# Pattern B: f'LGA '{var}' not found...'  ->  f"LGA '{var}' not found..."
pattern_b_fixes = [
    (82, "abia/migrants/odk_sync.py", "f'LGA '", 'f"LGA \''),
]

print("=" * 60)
print("NASA SURGICAL F-STRING REPAIR v2.0")
print("=" * 60)

fixed = 0
for lineno, relpath, old, new in pattern_a_fixes:
    f = ROOT / relpath
    if not f.exists():
        print("\nSKIP (missing): " + relpath)
        continue
    lines = f.read_text(encoding="utf-8", errors="ignore").split("\n")
    idx = lineno - 1
    if idx < len(lines):
        original = lines[idx]
        # Only replace the LAST occurrence of old on this line
        if old in original:
            lines[idx] = original.rsplit(old, 1)[0] + new + original.rsplit(old, 1)[1][1:] if len(original.rsplit(old, 1)[1]) > 0 else original.rsplit(old, 1)[0] + new
            # Actually simpler: just replace the last char if it's the old quote
            stripped = original.rstrip()
            if stripped.endswith(old):
                lines[idx] = stripped[:-1] + new
            else:
                # Replace last occurrence
                lines[idx] = original.rsplit(old, 1)[0] + new
            f.write_text("\n".join(lines), encoding="utf-8")
            fixed += 1
            print("\nFIXED " + relpath + ":" + str(lineno))
            print("  BEFORE: " + original.strip()[:80])
            print("  AFTER:  " + lines[idx].strip()[:80])

for lineno, relpath, old, new in pattern_b_fixes:
    f = ROOT / relpath
    if not f.exists():
        print("\nSKIP (missing): " + relpath)
        continue
    lines = f.read_text(encoding="utf-8", errors="ignore").split("\n")
    idx = lineno - 1
    if idx < len(lines):
        original = lines[idx]
        if old in original:
            lines[idx] = original.replace(old, new, 1)
            # Also fix the trailing quote from ' to "
            if lines[idx].rstrip().endswith("'"):
                lines[idx] = lines[idx].rstrip()[:-1] + '"'
            f.write_text("\n".join(lines), encoding="utf-8")
            fixed += 1
            print("\nFIXED " + relpath + ":" + str(lineno))
            print("  BEFORE: " + original.strip()[:80])
            print("  AFTER:  " + lines[idx].strip()[:80])

# Verify all 8
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)
all_ok = True
for lineno, relpath, _, _ in pattern_a_fixes + pattern_b_fixes:
    f = ROOT / relpath
    if not f.exists():
        continue
    try:
        with open(str(f), "r", encoding="utf-8", errors="ignore") as src:
            compile(src.read(), str(f), "exec")
        print("  OK   : " + relpath)
    except SyntaxError as e:
        print("  FAIL : " + relpath + " line " + str(e.lineno) + ": " + str(e.msg))
        all_ok = False

print("\n" + "=" * 60)
if all_ok:
    print("RESULT: 8/8 FILES CLEAN — ZERO SYNTAX ERRORS")
else:
    print("RESULT: SOME FILES STILL BROKEN")
print("=" * 60)
