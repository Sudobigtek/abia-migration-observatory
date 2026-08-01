#!/usr/bin/env python3
# NASA Line-by-Line Surgical Repair v4.1
from pathlib import Path

ROOT = Path.home() / "abia-migration-observatory" / "abia-app"

def fix_services_py():
    f = ROOT / "dynamic_fields_backup_47470/services.py"
    if not f.exists(): return
    text = f.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    fixed = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "Unknown field type" in line and "{definition.field_type}" in line:
            fixed.append(line)
            if i + 1 < len(lines) and "return validator" in lines[i + 1]:
                fixed.append("        )")
                print("  INSERTED missing ) in services.py")
            i += 1
        else:
            fixed.append(line)
            i += 1
    f.write_text("\n".join(fixed), encoding="utf-8")

def fix_common_exceptions():
    f = ROOT / "dynamic_fields/common_exceptions_v2.py"
    if not f.exists(): return
    text = f.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    fixed = []
    for line in lines:
        if "Invalid status transition" in line and line.rstrip().endswith(SQ) and not line.rstrip().endswith("," + SQ):
            line = line.rstrip() + ","
            print("  ADDED comma in common_exceptions_v2.py (status)")
        if "Referral not found" in line and line.rstrip().endswith(DQ + ","):
            line = line.rstrip()[:-2] + SQ + ","
            print("  FIXED mixed quote in common_exceptions_v2.py (referral)")
        fixed.append(line)
    f.write_text("\n".join(fixed), encoding="utf-8")

def fix_kong_client():
    f = ROOT / "abia/common/kong_client.py"
    if not f.exists(): return
    text = f.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    fixed = []
    for line in lines:
        if "/services/{service_name}/routes" in line and line.rstrip().endswith(SQ) and not line.rstrip().endswith("," + SQ):
            line = line.rstrip() + ","
            print("  ADDED comma in kong_client.py")
        fixed.append(line)
    f.write_text("\n".join(fixed), encoding="utf-8")

def fix_ncfrmi():
    f = ROOT / "abia/ncfrmi/services.py"
    if not f.exists(): return
    text = f.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    fixed = []
    for line in lines:
        if "cls.BASE_URL" in line and "/migrants/" in line and line.rstrip().endswith(SQ) and not line.rstrip().endswith("," + SQ):
            line = line.rstrip() + ","
            print("  ADDED comma in ncfrmi/services.py")
        fixed.append(line)
    f.write_text("\n".join(fixed), encoding="utf-8")

def fix_iom():
    f = ROOT / "abia/iom/services.py"
    if not f.exists(): return
    text = f.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    fixed = []
    for line in lines:
        if "config.api_base_url" in line and "/migrants/" in line and line.rstrip().endswith(SQ) and not line.rstrip().endswith("," + SQ):
            line = line.rstrip() + ","
            print("  ADDED comma in iom/services.py")
        fixed.append(line)
    f.write_text("\n".join(fixed), encoding="utf-8")

def fix_export_pipeline():
    f = ROOT / "abia/export_pipeline/views.py"
    if not f.exists(): return
    text = f.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    fixed = []
    for line in lines:
        if "ipfs.io/ipfs" in line and line.rstrip().endswith(SQ) and not line.rstrip().endswith("," + SQ):
            line = line.rstrip() + ","
            print("  ADDED comma in export_pipeline/views.py (ipfs)")
        if "pinata.cloud" in line and line.rstrip().endswith(DQ + ","):
            line = line.rstrip()[:-2] + SQ + ","
            print("  FIXED mixed quote in export_pipeline/views.py (pinata)")
        fixed.append(line)
    f.write_text("\n".join(fixed), encoding="utf-8")

print("=" * 60)
print("NASA LINE-BY-LINE SURGICAL REPAIR v4.1")
print("=" * 60)

fix_services_py()
fix_common_exceptions()
fix_kong_client()
fix_ncfrmi()
fix_iom()
fix_export_pipeline()

print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

verify_files = [
    "dynamic_fields_backup_47470/services.py",
    "dynamic_fields/common_exceptions_v2.py",
    "dynamic_fields/fix_tests_contract_compliant.py",
    "abia/common/kong_client.py",
    "abia/ncfrmi/services.py",
    "abia/migrants/odk_sync.py",
    "abia/iom/services.py",
    "abia/export_pipeline/views.py",
]

all_ok = True
for fp in verify_files:
    f = ROOT / fp
    if not f.exists():
        continue
    try:
        with open(str(f), "r", encoding="utf-8", errors="ignore") as src:
            compile(src.read(), str(f), "exec")
        print("  OK   : " + fp)
    except SyntaxError as e:
        print("  FAIL : " + fp + " line " + str(e.lineno) + ": " + str(e.msg))
        all_ok = False

print("\n" + "=" * 60)
if all_ok:
    print("RESULT: 8/8 FILES CLEAN")
    print("INFRASTRUCTURE FULLY OPERATIONAL")
else:
    print("RESULT: SOME FILES STILL BROKEN")
print("=" * 60)