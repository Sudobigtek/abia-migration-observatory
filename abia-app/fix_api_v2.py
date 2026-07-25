#!/usr/bin/env python3
"""
AMO API Schema Fix Script v2.5-BULLETPROOF
Restores corrupted files from git, then applies clean fixes.
Run: cd /home/abia/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 fix_api_v2.py
"""

import os, re, shutil, subprocess

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# ========================================================================
# STEP 0: GIT RESTORE CORRUPTED FILES
# ========================================================================
print("=== STEP 0: Restore corrupted files from git ===")

corrupted = [
    "abia/common/views.py",
    "abia/common/gateway.py",
    "abia/analytics/views.py",
    "abia/audit/views.py",
    "abia/backup/views.py",
    "abia/cbn/views.py",
    "abia/charts/views.py",
    "abia/webhooks/views.py",
    "abia/worldbank/views.py",
    "abia/wto/views.py",
]

for f in corrupted:
    if os.path.exists(f):
        out, err, rc = run(f"git checkout -- {f}")
        if rc == 0:
            print(f"  RESTORED: {f}")
        else:
            print(f"  FAIL: {f} - {err}")
    else:
        print(f"  SKIP: {f} not found")

# ========================================================================
# STEP 1: CREATE CENTRAL RESPONSE SERIALIZERS FILE
# ========================================================================
print("\n=== STEP 1: Create central response serializers ===")

os.makedirs("abia/common", exist_ok=True)

serializers_py = """from rest_framework import serializers


class CacheStatsResponse(serializers.Serializer):
    hits = serializers.IntegerField()
    misses = serializers.IntegerField()
    keys = serializers.IntegerField()


class ApiVersionInfoResponse(serializers.Serializer):
    version = serializers.CharField()
    build = serializers.CharField()


class AnalyticsCasesByLgaResponse(serializers.Serializer):
    results = serializers.ListField(child=serializers.DictField())
    total = serializers.IntegerField()


class AnalyticsCasesByTypeResponse(serializers.Serializer):
    results = serializers.ListField(child=serializers.DictField())
    total = serializers.IntegerField()


class AnalyticsDashboardResponse(serializers.Serializer):
    metrics = serializers.DictField()
    generated_at = serializers.DateTimeField()


class AnalyticsMonthlyTrendsResponse(serializers.Serializer):
    months = serializers.ListField(child=serializers.CharField())
    counts = serializers.ListField(child=serializers.IntegerField())


class AnalyticsOverviewResponse(serializers.Serializer):
    total_cases = serializers.IntegerField()
    total_migrants = serializers.IntegerField()
    open_cases = serializers.IntegerField()


class AnalyticsRecentActivityResponse(serializers.Serializer):
    activities = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()


class AnalyticsRiskDistributionResponse(serializers.Serializer):
    low = serializers.IntegerField()
    medium = serializers.IntegerField()
    high = serializers.IntegerField()
    critical = serializers.IntegerField()


class GenerateReportResponse(serializers.Serializer):
    report_id = serializers.CharField()
    status = serializers.CharField()
    url = serializers.CharField()


class BackupFilesResponse(serializers.Serializer):
    files = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()


class TriggerRestoreResponse(serializers.Serializer):
    job_id = serializers.CharField()
    status = serializers.CharField()


class BackupStatusResponse(serializers.Serializer):
    last_backup = serializers.DateTimeField()
    status = serializers.CharField()


class TriggerBackupResponse(serializers.Serializer):
    job_id = serializers.CharField()
    status = serializers.CharField()


class RemittanceByChannelResponse(serializers.Serializer):
    channels = serializers.ListField(child=serializers.DictField())
    total_naira = serializers.FloatField()


class RemittanceByLgaResponse(serializers.Serializer):
    lgas = serializers.ListField(child=serializers.DictField())
    total_naira = serializers.FloatField()


class RemittanceSummaryResponse(serializers.Serializer):
    total_inflows = serializers.FloatField()
    count = serializers.IntegerField()
    period = serializers.CharField()


class RemittanceTrendsResponse(serializers.Serializer):
    trends = serializers.ListField(child=serializers.DictField())
    currency = serializers.CharField()


class ChartDataResponse(serializers.Serializer):
    chart_id = serializers.CharField()
    data = serializers.DictField()


class PresetChartsResponse(serializers.Serializer):
    charts = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()


class AnalyticsSummaryResponse(serializers.Serializer):
    summary = serializers.DictField()
    generated_at = serializers.DateTimeField()


class GatewayKeyRotateResponse(serializers.Serializer):
    success = serializers.BooleanField()
    key_id = serializers.CharField()


class GatewayRoutesResponse(serializers.Serializer):
    routes = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()


class GatewayStatusResponse(serializers.Serializer):
    status = serializers.CharField()
    version = serializers.CharField()


class RetryFailedResponse(serializers.Serializer):
    retried = serializers.IntegerField()
    failed_ids = serializers.ListField(child=serializers.CharField())


class WebhookStatsResponse(serializers.Serializer):
    total = serializers.IntegerField()
    success_rate = serializers.FloatField()


class TriggerEventResponse(serializers.Serializer):
    event_id = serializers.CharField()
    status = serializers.CharField()


class MigrationIndicatorsResponse(serializers.Serializer):
    indicators = serializers.ListField(child=serializers.DictField())
    source = serializers.CharField()


class RemittanceIndicatorsResponse(serializers.Serializer):
    indicators = serializers.ListField(child=serializers.DictField())
    currency = serializers.CharField()


class IndicatorTrendResponse(serializers.Serializer):
    trend = serializers.ListField(child=serializers.DictField())
    indicator_code = serializers.CharField()


class TradeBalanceResponse(serializers.Serializer):
    balance = serializers.FloatField()
    period = serializers.CharField()


class LabourIntensiveTradeResponse(serializers.Serializer):
    sectors = serializers.ListField(child=serializers.DictField())
    total_value = serializers.FloatField()


class TopPartnersResponse(serializers.Serializer):
    partners = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()


class YearlySummaryResponse(serializers.Serializer):
    years = serializers.ListField(child=serializers.CharField())
    summary = serializers.DictField()
"""

write("abia/common/response_serializers.py", serializers_py)
print("  Created 34 response serializer classes.")

# ========================================================================
# STEP 2: INJECT CLEAN DECORATORS INTO VIEW FILES
# ========================================================================
print("\n=== STEP 2: Inject clean extend_schema decorators ===")

# Map: filepath -> list of (function_name, tag, summary, serializer_class_name)
VIEW_MAP = {
    "abia/common/views.py": [
        ("cache_stats_view", "System", "Cache statistics", "CacheStatsResponse"),
        ("api_version_info", "System", "API version information", "ApiVersionInfoResponse"),
    ],
    "abia/analytics/views.py": [
        ("analytics_cases_by_lga", "Analytics", "Cases grouped by LGA", "AnalyticsCasesByLgaResponse"),
        ("analytics_cases_by_type", "Analytics", "Cases grouped by type", "AnalyticsCasesByTypeResponse"),
        ("analytics_dashboard", "Analytics", "Dashboard overview metrics", "AnalyticsDashboardResponse"),
        ("analytics_monthly_trends", "Analytics", "Monthly case/migrant trends", "AnalyticsMonthlyTrendsResponse"),
        ("analytics_overview", "Analytics", "High-level analytics overview", "AnalyticsOverviewResponse"),
        ("analytics_recent_activity", "Analytics", "Recent system activity feed", "AnalyticsRecentActivityResponse"),
        ("analytics_risk_distribution", "Analytics", "Risk level distribution", "AnalyticsRiskDistributionResponse"),
    ],
    "abia/audit/views.py": [
        ("generate_report", "Audit", "Generate audit report", "GenerateReportResponse"),
    ],
    "abia/backup/views.py": [
        ("backup_files", "System", "List backup files", "BackupFilesResponse"),
        ("trigger_restore", "System", "Trigger backup restore", "TriggerRestoreResponse"),
        ("backup_status", "System", "Backup system status", "BackupStatusResponse"),
        ("trigger_backup", "System", "Trigger manual backup", "TriggerBackupResponse"),
    ],
    "abia/cbn/views.py": [
        ("remittance_by_channel", "CBN", "Remittances by channel", "RemittanceByChannelResponse"),
        ("remittance_by_lga", "CBN", "Remittances by LGA", "RemittanceByLgaResponse"),
        ("remittance_summary", "CBN", "Remittance summary", "RemittanceSummaryResponse"),
        ("remittance_trends", "CBN", "Remittance trends over time", "RemittanceTrendsResponse"),
    ],
    "abia/charts/views.py": [
        ("chart_data", "Analytics", "Raw chart data", "ChartDataResponse"),
        ("preset_charts", "Analytics", "List preset chart configurations", "PresetChartsResponse"),
        ("analytics_summary", "Analytics", "Summary for analytics charts", "AnalyticsSummaryResponse"),
    ],
    "abia/common/gateway.py": [
        ("gateway_key_rotate", "System", "Rotate gateway API key", "GatewayKeyRotateResponse"),
        ("gateway_routes", "System", "List gateway routes", "GatewayRoutesResponse"),
        ("gateway_status", "System", "Gateway health status", "GatewayStatusResponse"),
    ],
    "abia/webhooks/views.py": [
        ("retry_failed", "Webhooks", "Retry failed webhook deliveries", "RetryFailedResponse"),
        ("webhook_stats", "Webhooks", "Webhook delivery statistics", "WebhookStatsResponse"),
        ("trigger_event", "Webhooks", "Trigger webhook event manually", "TriggerEventResponse"),
    ],
    "abia/worldbank/views.py": [
        ("migration_indicators", "World Bank", "Migration indicators from World Bank", "MigrationIndicatorsResponse"),
        ("remittance_indicators", "World Bank", "Remittance indicators from World Bank", "RemittanceIndicatorsResponse"),
        ("indicator_trend", "World Bank", "World Bank indicator trend over time", "IndicatorTrendResponse"),
    ],
    "abia/wto/views.py": [
        ("trade_balance", "WTO", "Trade balance indicators", "TradeBalanceResponse"),
        ("labour_intensive_trade", "WTO", "Labour-intensive trade data", "LabourIntensiveTradeResponse"),
        ("top_partners", "WTO", "Top trading partners", "TopPartnersResponse"),
        ("yearly_summary", "WTO", "Yearly trade summary", "YearlySummaryResponse"),
    ],
}

total_fixed = 0

for path, views in VIEW_MAP.items():
    if not os.path.exists(path):
        print(f"  SKIP: {path} not found")
        continue

    content = read(path)
    lines = content.split("\n")
    modified = False

    # Add imports if missing
    has_extend = any("from drf_spectacular.utils import" in line and "extend_schema" in line for line in lines)
    has_serializers = any("from abia.common.response_serializers import" in line for line in lines)

    import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            import_idx = i + 1

    if not has_extend:
        lines.insert(import_idx, "from drf_spectacular.utils import extend_schema")
        import_idx += 1
        modified = True

    if not has_serializers:
        lines.insert(import_idx, "from abia.common.response_serializers import (")
        import_idx += 1
        # Add all serializer names used in this file
        serializer_names = sorted(set(v[3] for v in views))
        for name in serializer_names:
            lines.insert(import_idx, f"    {name},")
            import_idx += 1
        lines.insert(import_idx, ")")
        import_idx += 1
        modified = True

    for func_name, tag, summary, serializer_name in views:
        decorator = f"""@extend_schema(
    responses={serializer_name},
    tags=["{tag}"],
    summary="{summary}",
    description="Auto-documented endpoint. Replace with actual response shape if needed.",
)"""

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(f"def {func_name}(") and not stripped.startswith(f"def {func_name}_"):
                # Check if already decorated
                already = False
                for j in range(max(0, i-8), i):
                    if "@extend_schema" in lines[j] and func_name in lines[j+1:j+8].__str__():
                        already = True
                        break
                # Simpler check: look at previous non-empty line
                prev_idx = i - 1
                while prev_idx >= 0 and not lines[prev_idx].strip():
                    prev_idx -= 1
                if prev_idx >= 0 and "@extend_schema" in lines[prev_idx]:
                    already = True

                if already:
                    break

                indent = len(line) - len(line.lstrip())
                dec_lines = decorator.split("\n")
                for dl in reversed(dec_lines):
                    if dl.strip():
                        lines.insert(i, " " * indent + dl)
                    else:
                        lines.insert(i, dl)
                modified = True
                total_fixed += 1
                print(f"  Annotated {func_name} -> {serializer_name}")
                break

    if modified:
        write(path, "\n".join(lines))
    else:
        print(f"  No changes for {path}")

print(f"\n  Total views annotated: {total_fixed}")

# ========================================================================
# STEP 3: FIX CASEVIEWSET AND TYPE HINTS (from Phase 1)
# ========================================================================
print("\n=== STEP 3: Fix CaseViewSet and type hints ===")

# Fix CaseViewSet
cvp = "abia/cases/views.py"
if os.path.exists(cvp):
    c = read(cvp)
    if "class CaseViewSet" in c and "swagger_fake_view" not in c:
        if "queryset =" not in c.split("class CaseViewSet")[1].split("\ndef ")[0].split("\nclass ")[0]:
            c = c.replace(
                "class CaseViewSet(viewsets.ModelViewSet):",
                "class CaseViewSet(viewsets.ModelViewSet):\n    queryset = Case.objects.none()"
            )
        if "def get_queryset(self):" in c:
            c = re.sub(
                r'(    def get_queryset\(self\):)',
                r"\1\n        if getattr(self, 'swagger_fake_view', False):\n            return Case.objects.none()\n        if not self.request.user.is_authenticated:\n            return Case.objects.none()",
                c
            )
        else:
            c = re.sub(
                r'(class CaseViewSet\(viewsets\.ModelViewSet\):.*?)\n    def ',
                r"\1\n\n    def get_queryset(self):\n        if getattr(self, 'swagger_fake_view', False):\n            return Case.objects.none()\n        if not self.request.user.is_authenticated:\n            return Case.objects.none()\n        return Case.objects.all()  # TODO: refine with role logic\n\n    def ",
                c,
                flags=re.DOTALL
            )
        write(cvp, c)
        print("  Fixed CaseViewSet.")
    else:
        print("  CaseViewSet already guarded or not found.")

# Fix cases serializers type hints
csp = "abia/cases/serializers.py"
if os.path.exists(csp):
    c = read(csp)
    modified = False
    imports = []
    if "extend_schema_field" not in c:
        imports.append("from drf_spectacular.utils import extend_schema_field")
    if "Optional" not in c:
        imports.append("from typing import Optional, List, Dict, Any")
    if "import json" not in c:
        imports.append("import json")
    if imports:
        lines = c.split("\n")
        last_imp = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                last_imp = i + 1
        for imp in reversed(imports):
            lines.insert(last_imp, imp)
        c = "\n".join(lines)
        modified = True

    replacements = [
        ("def get_days_open(self, obj):",
         '@extend_schema_field(serializers.IntegerField(help_text="Days since case opened"))\n    def get_days_open(self, obj) -> Optional[int]:'),
        ("def get_location_geojson(self, obj):",
         '@extend_schema_field(serializers.DictField(help_text="GeoJSON Point object"))\n    def get_location_geojson(self, obj) -> Optional[Dict[str, Any]]:'),
        ("def get_referrals(self, obj):",
         '@extend_schema_field(serializers.ListField(child=serializers.DictField()))\n    def get_referrals(self, obj) -> List[Dict[str, Any]]:'),
    ]
    for old, new in replacements:
        if old in c and new.split("\n")[0] not in c:
            c = c.replace(old, new)
            modified = True

    if modified:
        write(csp, c)
    else:
        print("  cases/serializers.py: no changes needed.")

# Fix migrants serializers type hints
msp = "abia/migrants/serializers.py"
if os.path.exists(msp):
    c = read(msp)
    modified = False
    imports = []
    if "extend_schema_field" not in c:
        imports.append("from drf_spectacular.utils import extend_schema_field")
    if "Optional" not in c:
        imports.append("from typing import Optional")
    if imports:
        lines = c.split("\n")
        last_imp = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                last_imp = i + 1
        for imp in reversed(imports):
            lines.insert(last_imp, imp)
        c = "\n".join(lines)
        modified = True

    if "def get_age(self, obj):" in c:
        if "@extend_schema_field" not in c.split("def get_age")[0].split("\ndef ")[-1]:
            c = c.replace(
                "def get_age(self, obj):",
                '@extend_schema_field(serializers.IntegerField(help_text="Age in years"))\n    def get_age(self, obj) -> Optional[int]:'
            )
            modified = True

    if modified:
        write(msp, c)
    else:
        print("  migrants/serializers.py: no changes needed.")

# ========================================================================
# STEP 4: REMOVE DISABLE_ERRORS_AND_WARNINGS
# ========================================================================
print("\n=== STEP 4: Remove DISABLE_ERRORS_AND_WARNINGS ===")

settings_candidates = ["abia/settings.py", "abia/settings/base.py"]
settings_path = None
for sp in settings_candidates:
    if os.path.exists(sp):
        settings_path = sp
        break

if settings_path:
    c = read(settings_path)
    if "DISABLE_ERRORS_AND_WARNINGS" in c:
        c = re.sub(r"['\"]DISABLE_ERRORS_AND_WARNINGS['\"]\s*:\s*True\s*,?\s*\n?", "", c)
        write(settings_path, c)
        print("  Removed DISABLE_ERRORS_AND_WARNINGS.")
    else:
        print("  Already clean.")
else:
    print("  No settings file found.")

# ========================================================================
# STEP 5: CLEAR CACHE
# ========================================================================
print("\n=== STEP 5: Clear Cache ===")
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
print("FIX SCRIPT V2.5 COMPLETE.")
print("Next: Restart Django server, then run validation.")
print("="*60)
