#!/usr/bin/env python3
"""
AMO API Schema Fix Script v2.5
Fixes all hidden APIViews, ViewSet guards, and enum collisions.
Run: cd /home/abia/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 fix_api.py
"""

import os, re, shutil

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

def add_imports(content, needed):
    lines = content.split("\n")
    last_imp = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_imp = i + 1
    for imp in reversed(needed):
        if imp not in content:
            lines.insert(last_imp, imp)
    return "\n".join(lines)

# ========================================================================
# PART 1: FIX APIVIEWS
# ========================================================================
print("=== PART 1: Fix APIViews ===")

APIVIEW_FIXES = {
    "abia/common/views.py": [
        ("cache_stats_view", "System", "Cache statistics", {"hits": "IntegerField", "misses": "IntegerField", "keys": "IntegerField"}),
        ("api_version_info", "System", "API version information", {"version": "CharField", "build": "CharField"}),
    ],
    "abia/analytics/views.py": [
        ("analytics_cases_by_lga", "Analytics", "Cases grouped by LGA", {"results": "ListField", "total": "IntegerField"}),
        ("analytics_cases_by_type", "Analytics", "Cases grouped by type", {"results": "ListField", "total": "IntegerField"}),
        ("analytics_dashboard", "Analytics", "Dashboard overview metrics", {"metrics": "DictField", "generated_at": "DateTimeField"}),
        ("analytics_monthly_trends", "Analytics", "Monthly case/migrant trends", {"months": "ListField", "counts": "ListField"}),
        ("analytics_overview", "Analytics", "High-level analytics overview", {"total_cases": "IntegerField", "total_migrants": "IntegerField", "open_cases": "IntegerField"}),
        ("analytics_recent_activity", "Analytics", "Recent system activity feed", {"activities": "ListField", "count": "IntegerField"}),
        ("analytics_risk_distribution", "Analytics", "Risk level distribution", {"low": "IntegerField", "medium": "IntegerField", "high": "IntegerField", "critical": "IntegerField"}),
    ],
    "abia/audit/views.py": [
        ("generate_report", "Audit", "Generate audit report", {"report_id": "CharField", "status": "CharField", "url": "CharField"}),
    ],
    "abia/backup/views.py": [
        ("backup_files", "System", "List backup files", {"files": "ListField", "count": "IntegerField"}),
        ("trigger_restore", "System", "Trigger backup restore", {"job_id": "CharField", "status": "CharField"}),
        ("backup_status", "System", "Backup system status", {"last_backup": "DateTimeField", "status": "CharField"}),
        ("trigger_backup", "System", "Trigger manual backup", {"job_id": "CharField", "status": "CharField"}),
    ],
    "abia/cbn/views.py": [
        ("remittance_by_channel", "CBN", "Remittances by channel", {"channels": "ListField", "total_naira": "FloatField"}),
        ("remittance_by_lga", "CBN", "Remittances by LGA", {"lgas": "ListField", "total_naira": "FloatField"}),
        ("remittance_summary", "CBN", "Remittance summary", {"total_inflows": "FloatField", "count": "IntegerField", "period": "CharField"}),
        ("remittance_trends", "CBN", "Remittance trends over time", {"trends": "ListField", "currency": "CharField"}),
    ],
    "abia/charts/views.py": [
        ("chart_data", "Analytics", "Raw chart data", {"chart_id": "CharField", "data": "DictField"}),
        ("preset_charts", "Analytics", "List preset chart configurations", {"charts": "ListField", "count": "IntegerField"}),
        ("analytics_summary", "Analytics", "Summary for analytics charts", {"summary": "DictField", "generated_at": "DateTimeField"}),
    ],
    "abia/common/gateway.py": [
        ("gateway_key_rotate", "System", "Rotate gateway API key", {"success": "BooleanField", "key_id": "CharField"}),
        ("gateway_routes", "System", "List gateway routes", {"routes": "ListField", "count": "IntegerField"}),
        ("gateway_status", "System", "Gateway health status", {"status": "CharField", "version": "CharField"}),
    ],
    "abia/webhooks/views.py": [
        ("retry_failed", "Webhooks", "Retry failed webhook deliveries", {"retried": "IntegerField", "failed_ids": "ListField"}),
        ("webhook_stats", "Webhooks", "Webhook delivery statistics", {"total": "IntegerField", "success_rate": "FloatField"}),
        ("trigger_event", "Webhooks", "Trigger webhook event manually", {"event_id": "CharField", "status": "CharField"}),
    ],
    "abia/worldbank/views.py": [
        ("migration_indicators", "World Bank", "Migration indicators from World Bank", {"indicators": "ListField", "source": "CharField"}),
        ("remittance_indicators", "World Bank", "Remittance indicators from World Bank", {"indicators": "ListField", "currency": "CharField"}),
        ("indicator_trend", "World Bank", "World Bank indicator trend over time", {"trend": "ListField", "indicator_code": "CharField"}),
    ],
    "abia/wto/views.py": [
        ("trade_balance", "WTO", "Trade balance indicators", {"balance": "FloatField", "period": "CharField"}),
        ("labour_intensive_trade", "WTO", "Labour-intensive trade data", {"sectors": "ListField", "total_value": "FloatField"}),
        ("top_partners", "WTO", "Top trading partners", {"partners": "ListField", "count": "IntegerField"}),
        ("yearly_summary", "WTO", "Yearly trade summary", {"years": "ListField", "summary": "DictField"}),
    ],
}

total_views = 0

for path, views in APIVIEW_FIXES.items():
    if not os.path.exists(path):
        print("  SKIP:", path, "not found")
        continue

    content = read(path)
    lines = content.split("\n")
    modified = False

    needed = []
    if not any("from drf_spectacular.utils import" in line and "extend_schema" in line for line in lines):
        needed.append("from drf_spectacular.utils import extend_schema, inline_serializer")
    if not any("from rest_framework import serializers" in line for line in lines):
        needed.append("from rest_framework import serializers")
    if needed:
        lines = add_imports("\n".join(lines), needed).split("\n")
        modified = True

    for func_name, tag, summary, fields in views:
        field_lines = []
        for k, v in fields.items():
            field_lines.append(f"            '{k}': serializers.{v}(),")
        fields_str = "\n".join(field_lines)
        serializer_name = "".join([w.capitalize() for w in func_name.split("_")]) + "Response"

        decorator_lines = [
            "@extend_schema(",
            f"    responses=inline_serializer('{serializer_name}', fields={{",
            fields_str,
            "        }}),",
            f"    tags=['{tag}'],",
            f"    summary='{summary}',",
            "    description='Auto-documented endpoint. Replace with actual response shape if needed.',",
            ")",
        ]

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(f"def {func_name}(") and not stripped.startswith(f"def {func_name}_"):
                if i > 0 and "@extend_schema" in lines[i-1]:
                    break
                indent = len(line) - len(line.lstrip())
                for dl in reversed(decorator_lines):
                    if dl.strip():
                        lines.insert(i, " " * indent + dl)
                    else:
                        lines.insert(i, dl)
                modified = True
                total_views += 1
                print(f"  Annotated {func_name} in {path}")
                break

    if modified:
        write(path, "\n".join(lines))
    else:
        print("  No changes for", path)

print(f"\n  Total APIViews annotated: {total_views}")

# ========================================================================
# PART 2: FIX VIEWSETS
# ========================================================================
print("\n=== PART 2: Fix ViewSets ===")

VIEWSET_FIXES = [
    ("abia/workflows/views.py", "WorkflowInstanceViewSet", "WorkflowInstance"),
    ("abia/accounts/views.py", "UserViewSet", "User"),
]

for path, class_name, model_name in VIEWSET_FIXES:
    if not os.path.exists(path):
        print("  SKIP:", path, "not found")
        continue

    content = read(path)
    if class_name not in content:
        print("  SKIP:", class_name, "not in", path)
        continue

    if "swagger_fake_view" in content:
        print("  Already guarded:", class_name)
        continue

    class_marker = f"class {class_name}("
    idx = content.find(class_marker)
    if idx == -1:
        print("  Could not find class:", class_name)
        continue

    class_end = content.find("\n", idx)
    before = content[:class_end]
    after = content[class_end:]

    next_class = after.find("\nclass ")
    class_body = after[:next_class] if next_class != -1 else after

    if "queryset" not in class_body.split("\ndef ")[0]:
        guard_block = f"""
    queryset = {model_name}.objects.none()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return {model_name}.objects.none()
        if not self.request.user.is_authenticated:
            return {model_name}.objects.none()
        return super().get_queryset()"""
        content = before + guard_block + after
        write(path, content)
        print("  Guarded", class_name)
    else:
        print("  Queryset already exists for", class_name)

# ========================================================================
# PART 3: FIX ENUM COLLISIONS IN SETTINGS
# ========================================================================
print("\n=== PART 3: Fix Enum Collisions ===")

settings_candidates = ["abia/settings.py", "abia/settings/base.py"]
settings_path = None
for sp in settings_candidates:
    if os.path.exists(sp):
        settings_path = sp
        break

if settings_path:
    c = read(settings_path)
    if "ENUM_NAME_OVERRIDES" not in c:
        enum_block = """    'ENUM_NAME_OVERRIDES': {
        'StatusEnum': 'abia.cases.models.StatusChoices',
        'RoleEnum': 'abia.accounts.models.RoleChoices',
    },
"""
        idx = c.find("'SPECTACULAR_SETTINGS': {")
        if idx != -1:
            end = c.find("\n", idx)
            c = c[:end+1] + enum_block + c[end+1:]
            write(settings_path, c)
            print("  Added ENUM_NAME_OVERRIDES.")
        else:
            print("  Could not find SPECTACULAR_SETTINGS.")
    else:
        print("  Already has ENUM_NAME_OVERRIDES.")
else:
    print("  No settings file found.")

# ========================================================================
# PART 4: CLEAR CACHE
# ========================================================================
print("\n=== PART 4: Clear Cache ===")
for root, dirs, files in os.walk("."):
    for d in list(dirs):
        if d == "__pycache__":
            shutil.rmtree(os.path.join(root, d), ignore_errors=True)
            dirs.remove(d)
    for f in files:
        if f.endswith(".pyc"):
            os.remove(os.path.join(root, f))
print("  Cache cleared.")

print("\n" + "="*60)
print("FIX SCRIPT COMPLETE.")
print("Next: Restart Django server, then run:")
print('  python3 manage.py spectacular --file /tmp/schema.yml --validate 2>&1 | tail -20')
print("="*60)
