import os, re

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# =====================================================================
# 1. Create clean response_serializers.py with ALL classes
# =====================================================================
os.makedirs("abia/common", exist_ok=True)

serializers_content = """from rest_framework import serializers

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

class RateLimitResponse(serializers.Serializer):
    limit = serializers.IntegerField()
    remaining = serializers.IntegerField()

class ThrottleStatsResponse(serializers.Serializer):
    total_requests = serializers.IntegerField()
    throttled = serializers.IntegerField()

class PermissionsResponse(serializers.Serializer):
    permissions = serializers.ListField(child=serializers.CharField())

class TransferDestinationResponse(serializers.Serializer):
    destinations = serializers.ListField(child=serializers.DictField())
    total = serializers.IntegerField()

class TopAthletesResponse(serializers.Serializer):
    athletes = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class TalentExportResponse(serializers.Serializer):
    talent_value = serializers.FloatField()
    count = serializers.IntegerField()

class TalentMapResponse(serializers.Serializer):
    lgas = serializers.ListField(child=serializers.DictField())

class AthletesBySportResponse(serializers.Serializer):
    sports = serializers.ListField(child=serializers.DictField())
    total = serializers.IntegerField()

class SearchResponse(serializers.Serializer):
    results = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class SearchFacetsResponse(serializers.Serializer):
    facets = serializers.DictField()

class RebuildIndexResponse(serializers.Serializer):
    status = serializers.CharField()
    indexed = serializers.IntegerField()

class ReportTypesResponse(serializers.Serializer):
    types = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class QualityDashboardResponse(serializers.Serializer):
    checks = serializers.ListField(child=serializers.DictField())
    score = serializers.FloatField()

class RunChecksResponse(serializers.Serializer):
    passed = serializers.IntegerField()
    failed = serializers.IntegerField()

class UnreadCountResponse(serializers.Serializer):
    count = serializers.IntegerField()

class MarkReadResponse(serializers.Serializer):
    status = serializers.CharField()
    updated = serializers.IntegerField()

class BroadcastResponse(serializers.Serializer):
    status = serializers.CharField()
    recipients = serializers.IntegerField()

class MigrationCorridorsResponse(serializers.Serializer):
    corridors = serializers.ListField(child=serializers.DictField())
    total = serializers.IntegerField()

class MigrationBySectorResponse(serializers.Serializer):
    sectors = serializers.ListField(child=serializers.DictField())

class FreeMovementStatsResponse(serializers.Serializer):
    stats = serializers.DictField()

class IntraRegionalTradeResponse(serializers.Serializer):
    trade_volume = serializers.FloatField()
    sectors = serializers.ListField(child=serializers.DictField())

class LgaBoundariesResponse(serializers.Serializer):
    lgas = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class LgaDetailResponse(serializers.Serializer):
    lga = serializers.DictField()

class GeoHotspotsResponse(serializers.Serializer):
    hotspots = serializers.ListField(child=serializers.DictField())

class GeoHotspotsListResponse(serializers.Serializer):
    hotspots = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class HeatmapDataResponse(serializers.Serializer):
    heatmap = serializers.ListField(child=serializers.DictField())

class NearbyResponse(serializers.Serializer):
    nearby = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class MapDataResponse(serializers.Serializer):
    map_data = serializers.DictField()

class TriggerAnalysisResponse(serializers.Serializer):
    status = serializers.CharField()
    analysis_id = serializers.CharField()

class HotspotListResponse(serializers.Serializer):
    hotspots = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class UploadCsvResponse(serializers.Serializer):
    status = serializers.CharField()
    rows_imported = serializers.IntegerField()

class ImportTemplateResponse(serializers.Serializer):
    template = serializers.DictField()

class SyncStatusResponse(serializers.Serializer):
    status = serializers.CharField()
    last_sync = serializers.DateTimeField()

class SyncSingleResponse(serializers.Serializer):
    status = serializers.CharField()
    migrant_id = serializers.CharField()

class SyncHistoryResponse(serializers.Serializer):
    history = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class BulkSyncResponse(serializers.Serializer):
    status = serializers.CharField()
    synced = serializers.IntegerField()
    failed = serializers.IntegerField()

class SearchCasesResponse(serializers.Serializer):
    results = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class MapConfigResponse(serializers.Serializer):
    config = serializers.DictField()

class LGABoundariesResponse(serializers.Serializer):
    lgas = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()

class HotspotMapResponse(serializers.Serializer):
    hotspots = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()
"""

write("abia/common/response_serializers.py", serializers_content)

# =====================================================================
# 2. Define all view fixes
# =====================================================================
VIEW_FIXES = {
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
    "abia/throttle/views.py": [
        ("my_rate_limit", "RateLimitResponse", "System", "Get my rate limit"),
        ("throttle_stats", "ThrottleStatsResponse", "System", "Throttle statistics"),
    ],
    "abia/tenant/views.py": [
        ("my_permissions", "PermissionsResponse", "Tenant", "Get my permissions"),
    ],
    "abia/sports/views.py": [
        ("transfers_by_destination", "TransferDestinationResponse", "Sports", "Transfers by destination"),
        ("top_valued_athletes", "TopAthletesResponse", "Sports", "Top valued athletes"),
        ("talent_export_value", "TalentExportResponse", "Sports", "Talent export value"),
        ("lga_talent_map", "TalentMapResponse", "Sports", "LGA talent map"),
        ("athletes_by_sport", "AthletesBySportResponse", "Sports", "Athletes by sport"),
    ],
    "abia/search/views.py": [
        ("search", "SearchResponse", "Search", "Search across all entities"),
        ("search_facets", "SearchFacetsResponse", "Search", "Search facets"),
        ("rebuild_index", "RebuildIndexResponse", "Search", "Rebuild search index"),
    ],
    "abia/reports/views.py": [
        ("report_types", "ReportTypesResponse", "Reports", "List report types"),
        ("generate_report", "GenerateReportResponse", "Reports", "Generate report"),
    ],
    "abia/quality/views.py": [
        ("quality_dashboard", "QualityDashboardResponse", "Quality", "Quality dashboard"),
        ("run_checks", "RunChecksResponse", "Quality", "Run quality checks"),
    ],
    "abia/notifications/views.py": [
        ("unread_count", "UnreadCountResponse", "Notifications", "Unread notification count"),
        ("mark_read", "MarkReadResponse", "Notifications", "Mark notifications as read"),
        ("broadcast", "BroadcastResponse", "Notifications", "Broadcast notification"),
    ],
    "abia/ecowas/views.py": [
        ("migration_corridors", "MigrationCorridorsResponse", "ECOWAS", "Migration corridors"),
        ("migration_by_sector", "MigrationBySectorResponse", "ECOWAS", "Migration by sector"),
        ("free_movement_stats", "FreeMovementStatsResponse", "ECOWAS", "Free movement statistics"),
        ("intra_regional_trade", "IntraRegionalTradeResponse", "ECOWAS", "Intra-regional trade"),
    ],
    "abia/geo/views.py": [
        ("geo_lga_boundaries", "LgaBoundariesResponse", "Geo", "LGA boundaries"),
        ("geo_lga_detail", "LgaDetailResponse", "Geo", "LGA detail"),
        ("geo_hotspots", "GeoHotspotsResponse", "Geo", "Geo hotspots"),
        ("geo_hotspots_list", "GeoHotspotsListResponse", "Geo", "List geo hotspots"),
        ("geo_heatmap_data", "HeatmapDataResponse", "Geo", "Heatmap data"),
        ("geo_nearby", "NearbyResponse", "Geo", "Nearby locations"),
    ],
    "abia/hotspot/views.py": [
        ("map_data", "MapDataResponse", "Hotspots", "Map data"),
        ("trigger_analysis", "TriggerAnalysisResponse", "Hotspots", "Trigger hotspot analysis"),
        ("hotspot_list", "HotspotListResponse", "Hotspots", "List hotspots"),
    ],
    "abia/importers/views.py": [
        ("upload_csv", "UploadCsvResponse", "Importers", "Upload CSV"),
        ("import_template", "ImportTemplateResponse", "Importers", "Get import template"),
    ],
    "abia/ncfrmi/views.py": [
        ("sync_status", "SyncStatusResponse", "NCFRMI", "Sync status"),
        ("sync_single_migrant", "SyncSingleResponse", "NCFRMI", "Sync single migrant"),
        ("sync_history", "SyncHistoryResponse", "NCFRMI", "Sync history"),
        ("bulk_sync_migrants", "BulkSyncResponse", "NCFRMI", "Bulk sync migrants"),
    ],
    "abia/maps/views.py": [
        ("map_data", "MapDataResponse", "Maps", "Map data"),
        ("map_config", "MapConfigResponse", "Maps", "Map config"),
        ("lga_boundaries", "LGABoundariesResponse", "Maps", "LGA boundaries"),
        ("hotspot_map", "HotspotMapResponse", "Maps", "Hotspot map"),
    ],
    "abia/cases/search.py": [
        ("search_cases", "SearchCasesResponse", "Cases", "Search cases"),
    ],
}

for path, funcs in VIEW_FIXES.items():
    if not os.path.exists(path):
        print("  SKIP:", path)
        continue
    
    c = read(path)
    lines = c.split("\n")
    
    # Add imports at top
    insert_at = 1 if lines and lines[0].startswith("#!") else 0
    has_extend = any("from drf_spectacular.utils import" in l and "extend_schema" in l for l in lines)
    has_rs = any("from abia.common.response_serializers import" in l for l in lines)
    
    if not has_extend:
        lines.insert(insert_at, "from drf_spectacular.utils import extend_schema")
        insert_at += 1
    
    if not has_rs:
        names = sorted(set(f[1] for f in funcs))
        lines.insert(insert_at, "from abia.common.response_serializers import (")
        insert_at += 1
        for n in names:
            lines.insert(insert_at, f"    {n},")
            insert_at += 1
        lines.insert(insert_at, ")")
        insert_at += 1
    
    # Add decorators with duplicate detection
    for func_name, serializer, tag, summary in funcs:
        dec = f'@extend_schema(responses={serializer}, tags=["{tag}"], summary="{summary}")'
        
        for i, line in enumerate(lines):
            if line.strip().startswith(f"def {func_name}("):
                # Check if already decorated
                already = False
                for j in range(max(0, i-15), i):
                    if lines[j].strip().startswith("@extend_schema("):
                        between = lines[j+1:i]
                        if not any(l.strip().startswith("def ") for l in between):
                            already = True
                            break
                
                if already:
                    break
                
                # Insert before any existing decorators
                j = i
                while j > 0 and lines[j-1].strip().startswith("@"):
                    j -= 1
                lines.insert(j, dec)
                break
    
    write(path, "\n".join(lines))

# =====================================================================
# 3. Fix ViewSet queryset guards
# =====================================================================
for path, model_name in [
    ("abia/accounts/views.py", "User"),
    ("abia/workflows/views.py", "WorkflowInstance"),
]:
    if not os.path.exists(path):
        continue
    c = read(path)
    cls_name = path.split("/")[1].capitalize()
    if "swagger_fake_view" not in c:
        if "def get_queryset(self):" in c:
            c = re.sub(
                r'(    def get_queryset\(self\):)',
                r"\1\n        if getattr(self, 'swagger_fake_view', False):\n            return " + model_name + ".objects.none()",
                c
            )
        else:
            c = re.sub(
                r'(class ' + cls_name + r'ViewSet\([^)]+\):)',
                r"\1\n    queryset = " + model_name + ".objects.none()\n\n    def get_queryset(self):\n        if getattr(self, 'swagger_fake_view', False):\n            return " + model_name + ".objects.none()\n        return " + model_name + ".objects.all()",
                c
            )
        write(path, c)

print("\nDone. Run: python3 manage.py check && python3 manage.py spectacular --file /tmp/schema.yml --validate 2>&1 | tail -5")
