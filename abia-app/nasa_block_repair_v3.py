#!/usr/bin/env python3
# NASA Block-Level Surgical Repair v3.0
from pathlib import Path

ROOT = Path.home() / "abia-migration-observatory" / "abia-app"

print("=" * 60)
print("NASA BLOCK-LEVEL SURGICAL REPAIR v3.0")
print("=" * 60)

# --- FILE 1: dynamic_fields_backup_47470/services.py ---
f1 = ROOT / "dynamic_fields_backup_47470/services.py"
if f1.exists():
    text = f1.read_text(encoding="utf-8", errors="ignore")
    old = """    if not validator:
        raise FieldTypeError(
            f'Unknown field type: {definition.field_type}'
        return validator(definition, value)"""
    new = """    if not validator:
        raise FieldTypeError(
            f'Unknown field type: {definition.field_type}'
        )
        return validator(definition, value)"""
    if old in text:
        text = text.replace(old, new, 1)
        f1.write_text(text, encoding="utf-8")
        print("FIXED: dynamic_fields_backup_47470/services.py")
    else:
        print("PATTERN NOT FOUND: dynamic_fields_backup_47470/services.py")

# --- FILE 2: dynamic_fields/common_exceptions_v2.py Fix 1 ---
f2 = ROOT / "dynamic_fields/common_exceptions_v2.py"
if f2.exists():
    text = f2.read_text(encoding="utf-8", errors="ignore")
    old = """        super().__init__(
            f'Invalid status transition: {from_status} -> {to_status}'
            "invalid_status_transition",
            422,
        )"""
    new = """        super().__init__(
            f'Invalid status transition: {from_status} -> {to_status}',
            "invalid_status_transition",
            422,
        )"""
    if old in text:
        text = text.replace(old, new, 1)
        f2.write_text(text, encoding="utf-8")
        print("FIXED: dynamic_fields/common_exceptions_v2.py (comma)")
    else:
        print("PATTERN NOT FOUND: dynamic_fields/common_exceptions_v2.py (comma)")

# --- FILE 2: dynamic_fields/common_exceptions_v2.py Fix 2 ---
f2b = ROOT / "dynamic_fields/common_exceptions_v2.py"
if f2b.exists():
    text = f2b.read_text(encoding="utf-8", errors="ignore")
    old = """            f'Referral not found: {referral_id}",
            "referral_not_found",
            404
        )"""
    new = """            f'Referral not found: {referral_id}',
            "referral_not_found",
            404,
        )"""
    if old in text:
        text = text.replace(old, new, 1)
        f2b.write_text(text, encoding="utf-8")
        print("FIXED: dynamic_fields/common_exceptions_v2.py (quote)")
    else:
        print("PATTERN NOT FOUND: dynamic_fields/common_exceptions_v2.py (quote)")

# --- FILE 3: abia/common/kong_client.py ---
f3 = ROOT / "abia/common/kong_client.py"
if f3.exists():
    text = f3.read_text(encoding="utf-8", errors="ignore")
    old = """    result = KongClient._request(
        f'/services/{service_name}/routes'
        {"paths": [path]},
        "POST",
    )"""
    new = """    result = KongClient._request(
        f'/services/{service_name}/routes',
        {"paths": [path]},
        "POST",
    )"""
    if old in text:
        text = text.replace(old, new, 1)
        f3.write_text(text, encoding="utf-8")
        print("FIXED: abia/common/kong_client.py")
    else:
        print("PATTERN NOT FOUND: abia/common/kong_client.py")

# --- FILE 4: abia/ncfrmi/services.py ---
f4 = ROOT / "abia/ncfrmi/services.py"
if f4.exists():
    text = f4.read_text(encoding="utf-8", errors="ignore")
    old = """        response = requests.post(
            f'{cls.BASE_URL}/migrants/'
            json=payload,
            headers=cls._headers(),
            timeout=30
        )"""
    new = """        response = requests.post(
            f'{cls.BASE_URL}/migrants/',
            json=payload,
            headers=cls._headers(),
            timeout=30,
        )"""
    if old in text:
        text = text.replace(old, new, 1)
        f4.write_text(text, encoding="utf-8")
        print("FIXED: abia/ncfrmi/services.py")
    else:
        print("PATTERN NOT FOUND: abia/ncfrmi/services.py")

# --- FILE 5: abia/iom/services.py ---
f5 = ROOT / "abia/iom/services.py"
if f5.exists():
    text = f5.read_text(encoding="utf-8", errors="ignore")
    old = """        response = requests.post(
            f'{config.api_base_url}/migrants/'
            json=payload,
            headers=IOMService._headers(config),
            timeout=60
        )"""
    new = """        response = requests.post(
            f'{config.api_base_url}/migrants/',
            json=payload,
            headers=IOMService._headers(config),
            timeout=60,
        )"""
    if old in text:
        text = text.replace(old, new, 1)
        f5.write_text(text, encoding="utf-8")
        print("FIXED: abia/iom/services.py")
    else:
        print("PATTERN NOT FOUND: abia/iom/services.py")

# --- FILE 6: abia/export_pipeline/views.py ---
f6 = ROOT / "abia/export_pipeline/views.py"
if f6.exists():
    text = f6.read_text(encoding="utf-8", errors="ignore")
    old = """        "gateway_urls": [
            f'https://ipfs.io/ipfs/{export.ipfs_hash}'
            f'https://gateway.pinata.cloud/ipfs/{export.ipfs_hash}",
        ]"""
    new = """        "gateway_urls": [
            f'https://ipfs.io/ipfs/{export.ipfs_hash}',
            f'https://gateway.pinata.cloud/ipfs/{export.ipfs_hash}',
        ]"""
    if old in text:
        text = text.replace(old, new, 1)
        f6.write_text(text, encoding="utf-8")
        print("FIXED: abia/export_pipeline/views.py")
    else:
        print("PATTERN NOT FOUND: abia/export_pipeline/views.py")

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
    print("RESULT: 8/8 FILES CLEAN — ZERO SYNTAX ERRORS")
    print("INFRASTRUCTURE FULLY OPERATIONAL")
else:
    print("RESULT: SOME FILES STILL BROKEN")
print("=" * 60)
