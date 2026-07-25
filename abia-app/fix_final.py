import os

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# =====================================================================
# Add missing response classes
# =====================================================================
rs_path = "abia/common/response_serializers.py"
rs = read(rs_path) if os.path.exists(rs_path) else ""

missing = """
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

if "class SyncStatusResponse" not in rs:
    with open(rs_path, "a") as f:
        f.write(missing)
    print("  ADDED missing response classes")

# =====================================================================
# Fix all remaining files
# =====================================================================
fixes = {
    "abia/webhooks/views.py": [
        ("trigger_event", "TriggerEventResponse", "Webhooks", "Trigger webhook event manually"),
        ("retry_failed", "RetryFailedResponse", "Webhooks", "Retry failed webhook deliveries"),
    ],
    "abia/search/views.py": [
        ("rebuild_index", "RebuildIndexResponse", "Search", "Rebuild search index"),
    ],
    "abia/reports/views.py": [
        ("generate_report", "GenerateReportResponse", "Reports", "Generate report"),
    ],
    "abia/quality/views.py": [
        ("run_checks", "RunChecksResponse", "Quality", "Run quality checks"),
    ],
    "abia/notifications/views.py": [
        ("mark_read", "MarkReadResponse", "Notifications", "Mark notifications as read"),
        ("broadcast", "BroadcastResponse", "Notifications", "Broadcast notification"),
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
    "abia/hotspot/views.py": [
        ("trigger_analysis", "TriggerAnalysisResponse", "Hotspots", "Trigger hotspot analysis"),
    ],
    "abia/common/gateway.py": [
        ("gateway_key_rotate", "GatewayKeyRotateResponse", "System", "Rotate gateway API key"),
    ],
    "abia/backup/views.py": [
        ("trigger_restore", "TriggerRestoreResponse", "System", "Trigger backup restore"),
        ("trigger_backup", "TriggerBackupResponse", "System", "Trigger manual backup"),
    ],
    "abia/audit/views.py": [
        ("generate_report", "GenerateReportResponse", "Audit", "Generate audit report"),
    ],
    "abia/cases/search.py": [
        ("search_cases", "SearchCasesResponse", "Cases", "Search cases"),
    ],
}

for path, funcs in fixes.items():
    if not os.path.exists(path):
        print("  SKIP:", path)
        continue
    
    c = read(path)
    lines = c.split("\n")
    
    # Ensure imports exist
    has_extend = "from drf_spectacular.utils import extend_schema" in c
    has_rs = "from abia.common.response_serializers import" in c
    
    insert_at = 1 if lines and lines[0].startswith("#!") else 0
    
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
    
    # Add decorators only if missing
    for func_name, serializer, tag, summary in funcs:
        dec = f'@extend_schema(responses={serializer}, tags=["{tag}"], summary="{summary}")'
        
        for i, line in enumerate(lines):
            if line.strip().startswith(f"def {func_name}("):
                # Check if already decorated (look at previous non-empty line)
                prev = i - 1
                while prev >= 0 and not lines[prev].strip():
                    prev -= 1
                if prev >= 0 and "@extend_schema" in lines[prev]:
                    break
                
                # Insert before any existing decorators
                j = i
                while j > 0 and lines[j-1].strip().startswith("@"):
                    j -= 1
                lines.insert(j, dec)
                break
    
    write(path, "\n".join(lines))

print("\nDone. Run: python3 manage.py check && python3 manage.py spectacular --file /tmp/schema.yml --validate 2>&1 | tail -5")
