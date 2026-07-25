from rest_framework import serializers

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
