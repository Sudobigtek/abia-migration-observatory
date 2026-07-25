import os, re

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# Map: file -> list of (function_name, serializer_class_name)
fixes = {
    "abia/webhooks/views.py": [
        ("trigger_event", "TriggerEventResponse"),
        ("retry_failed", "RetryFailedResponse"),
    ],
    "abia/audit/views.py": [
        ("generate_report", "GenerateReportResponse"),
    ],
    "abia/backup/views.py": [
        ("trigger_backup", "TriggerBackupResponse"),
        ("trigger_restore", "TriggerRestoreResponse"),
    ],
    "abia/common/gateway.py": [
        ("gateway_key_rotate", "GatewayKeyRotateResponse"),
    ],
    "abia/hotspot/views.py": [
        ("trigger_analysis", "TriggerAnalysisResponse"),
    ],
    "abia/quality/views.py": [
        ("run_checks", "RunChecksResponse"),
    ],
    "abia/search/views.py": [
        ("rebuild_index", "RebuildIndexResponse"),
    ],
    "abia/notifications/views.py": [
        ("mark_read", "MarkReadResponse"),
        ("broadcast", "BroadcastResponse"),
    ],
    "abia/ncfrmi/views.py": [
        ("sync_single_migrant", "SyncSingleResponse"),
        ("bulk_sync_migrants", "BulkSyncResponse"),
    ],
    "abia/importers/views.py": [
        ("upload_csv", "UploadCsvResponse"),
    ],
}

for path, funcs in fixes.items():
    if not os.path.exists(path):
        continue
    
    c = read(path)
    lines = c.split("\n")
    
    # Add serializer_class assignments after each function
    for func_name, serializer in funcs:
        for i, line in enumerate(lines):
            if line.strip().startswith(f"def {func_name}("):
                # Find end of function
                j = i + 1
                indent = len(line) - len(line.lstrip())
                while j < len(lines):
                    next_line = lines[j]
                    if next_line.strip() and (len(next_line) - len(next_line.lstrip())) <= indent:
                        break
                    j += 1
                
                # Insert serializer_class assignment after function
                assignment = f"\n{func_name}.cls.serializer_class = {serializer}"
                if assignment.strip() not in c:
                    lines.insert(j, assignment)
                break
    
    write(path, "\n".join(lines))

print("\nDone. Run: python3 manage.py check && python3 manage.py spectacular --file /tmp/schema.yml --validate 2>&1 | tail -5")
