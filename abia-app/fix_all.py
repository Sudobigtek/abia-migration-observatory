import os

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# Create response serializers
os.makedirs("abia/common", exist_ok=True)
rs = read("abia/common/response_serializers.py") if os.path.exists("abia/common/response_serializers.py") else ""
if not rs:
    write("abia/common/response_serializers.py", """from rest_framework import serializers

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
""")

# Simple decorator injector
DECORATORS = {
    "abia/common/views.py": [
        ("cache_stats_view", "CacheStatsResponse", "System", "Cache statistics"),
        ("api_version_info", "ApiVersionInfoResponse", "System", "API version information"),
    ],
    "abia/analytics/views.py": [
        ("analytics_cases_by_lga", "AnalyticsCasesByLgaResponse", "Analytics", "Cases grouped by LGA"),
        ("analytics_cases_by_type", "AnalyticsCasesByTypeResponse", "Analytics", "Cases grouped by type"),
        ("analytics_dashboard", "AnalyticsDashboardResponse", "Analytics", "Dashboard overview metrics"),
        ("analytics_monthly_trends", "AnalyticsMonthlyTrendsResponse", "Analytics", "Monthly case/migrant trends"),
        ("analytics_overview", "AnalyticsOverviewResponse", "Analytics", "High-level analytics overview"),
        ("analytics_recent_activity", "AnalyticsRecentActivityResponse", "Analytics", "Recent system activity feed"),
        ("analytics_risk_distribution", "AnalyticsRiskDistributionResponse", "Analytics", "Risk level distribution"),
    ],
    "abia/audit/views.py": [
        ("generate_report", "GenerateReportResponse", "Audit", "Generate audit report"),
    ],
    "abia/backup/views.py": [
        ("backup_files", "BackupFilesResponse", "System", "List backup files"),
        ("trigger_restore", "TriggerRestoreResponse", "System", "Trigger backup restore"),
        ("backup_status", "BackupStatusResponse", "System", "Backup system status"),
        ("trigger_backup", "TriggerBackupResponse", "System", "Trigger manual backup"),
    ],
    "abia/cbn/views.py": [
        ("remittance_by_channel", "RemittanceByChannelResponse", "CBN", "Remittances by channel"),
        ("remittance_by_lga", "RemittanceByLgaResponse", "CBN", "Remittances by LGA"),
        ("remittance_summary", "RemittanceSummaryResponse", "CBN", "Remittance summary"),
        ("remittance_trends", "RemittanceTrendsResponse", "CBN", "Remittance trends over time"),
    ],
    "abia/charts/views.py": [
        ("chart_data", "ChartDataResponse", "Analytics", "Raw chart data"),
        ("preset_charts", "PresetChartsResponse", "Analytics", "List preset chart configurations"),
        ("analytics_summary", "AnalyticsSummaryResponse", "Analytics", "Summary for analytics charts"),
    ],
    "abia/common/gateway.py": [
        ("gateway_key_rotate", "GatewayKeyRotateResponse", "System", "Rotate gateway API key"),
        ("gateway_routes", "GatewayRoutesResponse", "System", "List gateway routes"),
        ("gateway_status", "GatewayStatusResponse", "System", "Gateway health status"),
    ],
    "abia/webhooks/views.py": [
        ("retry_failed", "RetryFailedResponse", "Webhooks", "Retry failed webhook deliveries"),
        ("webhook_stats", "WebhookStatsResponse", "Webhooks", "Webhook delivery statistics"),
        ("trigger_event", "TriggerEventResponse", "Webhooks", "Trigger webhook event manually"),
    ],
    "abia/worldbank/views.py": [
        ("migration_indicators", "MigrationIndicatorsResponse", "World Bank", "Migration indicators from World Bank"),
        ("remittance_indicators", "RemittanceIndicatorsResponse", "World Bank", "Remittance indicators from World Bank"),
        ("indicator_trend", "IndicatorTrendResponse", "World Bank", "World Bank indicator trend over time"),
    ],
    "abia/wto/views.py": [
        ("trade_balance", "TradeBalanceResponse", "WTO", "Trade balance indicators"),
        ("labour_intensive_trade", "LabourIntensiveTradeResponse", "WTO", "Labour-intensive trade data"),
        ("top_partners", "TopPartnersResponse", "WTO", "Top trading partners"),
        ("yearly_summary", "YearlySummaryResponse", "WTO", "Yearly trade summary"),
    ],
}

for path, views in DECORATORS.items():
    if not os.path.exists(path):
        continue
    c = read(path)
    lines = c.split("\n")

    # Insert imports at top (after shebang)
    insert_at = 1 if lines and lines[0].startswith("#!") else 0
    needs_extend = "from drf_spectacular.utils import extend_schema" not in c
    needs_serializers = "from abia.common.response_serializers import" not in c
    
    if needs_extend:
        lines.insert(insert_at, "from drf_spectacular.utils import extend_schema")
        insert_at += 1
    if needs_serializers:
        names = sorted(set(v[1] for v in views))
        lines.insert(insert_at, "from abia.common.response_serializers import (")
        insert_at += 1
        for n in names:
            lines.insert(insert_at, "    " + n + ",")
            insert_at += 1
        lines.insert(insert_at, ")")
        insert_at += 1

    # Insert decorators
    for func_name, serializer, tag, summary in views:
        dec = f'@extend_schema(responses={serializer}, tags=["{tag}"], summary="{summary}")'
        for i, line in enumerate(lines):
            if line.strip().startswith("def " + func_name + "("):
                # Check if already decorated
                if i > 0 and "@extend_schema" in lines[i-1]:
                    break
                # Move up past any existing decorators
                j = i
                while j > 0 and lines[j-1].strip().startswith("@"):
                    j -= 1
                lines.insert(j, dec)
                break

    write(path, "\n".join(lines))

print("\nDone. Now run: python3 manage.py check")
