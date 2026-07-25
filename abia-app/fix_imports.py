import os

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# Files and their missing response classes
fixes = {
    "abia/webhooks/views.py": ["TriggerEventResponse", "RetryFailedResponse"],
    "abia/search/views.py": ["RebuildIndexResponse"],
    "abia/reports/views.py": ["GenerateReportResponse"],
    "abia/quality/views.py": ["RunChecksResponse"],
    "abia/notifications/views.py": ["MarkReadResponse", "BroadcastResponse"],
    "abia/ncfrmi/views.py": ["SyncStatusResponse", "SyncSingleResponse", "SyncHistoryResponse", "BulkSyncResponse"],
    "abia/maps/views.py": ["MapDataResponse", "MapConfigResponse", "LGABoundariesResponse", "HotspotMapResponse"],
    "abia/hotspot/views.py": ["TriggerAnalysisResponse"],
    "abia/common/gateway.py": ["GatewayKeyRotateResponse"],
    "abia/backup/views.py": ["TriggerRestoreResponse", "TriggerBackupResponse"],
    "abia/audit/views.py": ["GenerateReportResponse"],
    "abia/cases/search.py": ["SearchCasesResponse"],
}

for path, classes in fixes.items():
    if not os.path.exists(path):
        print("  SKIP:", path)
        continue
    c = read(path)
    lines = c.split("\n")
    
    # Find existing import block
    import_idx = None
    for i, line in enumerate(lines):
        if "from abia.common.response_serializers import" in line:
            import_idx = i
            break
    
    if import_idx is None:
        # No import block at all — add one
        insert_at = 1 if lines and lines[0].startswith("#!") else 0
        lines.insert(insert_at, "from abia.common.response_serializers import (")
        insert_at += 1
        for cls in sorted(set(classes)):
            lines.insert(insert_at, f"    {cls},")
            insert_at += 1
        lines.insert(insert_at, ")")
    else:
        # Find closing paren of import block
        close_idx = import_idx + 1
        while close_idx < len(lines) and ")" not in lines[close_idx]:
            close_idx += 1
        existing = "\n".join(lines[import_idx:close_idx+1])
        for cls in classes:
            if cls not in existing:
                lines.insert(close_idx, f"    {cls},")
                close_idx += 1
    
    write(path, "\n".join(lines))

# =====================================================================
# Fix PostGIS fields: add explicit SerializerMethodField declarations
# =====================================================================

# cases/serializers.py
csp = "abia/cases/serializers.py"
if os.path.exists(csp):
    c = read(csp)
    if "location = serializers.SerializerMethodField()" not in c:
        c = c.replace(
            "location_geojson = serializers.SerializerMethodField()",
            "location = serializers.SerializerMethodField()\n    location_geojson = serializers.SerializerMethodField()"
        )
    if "from drf_spectacular.utils import extend_schema_field" not in c:
        c = "from drf_spectacular.utils import extend_schema_field\n" + c
    if "def get_location(self, obj)" in c:
        before = c.split("def get_location(self, obj)")[0].rsplit("def ", 1)[-1]
        if "@extend_schema_field" not in before:
            c = c.replace(
                "def get_location(self, obj)",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Point"))\n    def get_location(self, obj)'
            )
    write(csp, c)

# migrants/serializers.py — conservative fix
msp = "abia/migrants/serializers.py"
if os.path.exists(msp):
    c = read(msp)
    if "from drf_spectacular.utils import extend_schema_field" not in c:
        c = "from drf_spectacular.utils import extend_schema_field\n" + c
    # Only add explicit field declarations if they don't exist
    if "location = serializers" not in c and "gps_coordinates = serializers" not in c:
        if "class Meta:" in c:
            c = c.replace(
                "class Meta:",
                "location = serializers.SerializerMethodField()\n    gps_coordinates = serializers.SerializerMethodField()\n\n    class Meta:"
            )
    write(msp, c)

# accounts/serializers.py — conservative fix
asp = "abia/accounts/serializers.py"
if os.path.exists(asp):
    c = read(asp)
    if "from drf_spectacular.utils import extend_schema_field" not in c:
        c = "from drf_spectacular.utils import extend_schema_field\n" + c
    if "boundary = serializers" not in c:
        if "class Meta:" in c:
            c = c.replace(
                "class Meta:",
                "boundary = serializers.SerializerMethodField()\n\n    class Meta:"
            )
    write(asp, c)

print("\nDone. Run: python3 manage.py check && python3 manage.py spectacular --file /tmp/schema.yml --validate 2>&1 | tail -5")
