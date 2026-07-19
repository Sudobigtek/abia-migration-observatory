import csv, json, os
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import requests

@shared_task(bind=True, max_retries=2)
def generate_export(self, export_id):
    from .models import DataExport
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    from abia.referrals.models import Referral
    try:
        export = DataExport.objects.get(id=export_id)
    except DataExport.DoesNotExist:
        return {"status": "not_found"}
    export.status = "processing"
    export.save(update_fields=["status"])
    try:
        filters = export.filters or {}
        if export.entity_type == "migrants":
            queryset = Migrant.objects.all()
        elif export.entity_type == "cases":
            queryset = Case.objects.all()
        elif export.entity_type == "referrals":
            queryset = Referral.objects.all()
        else:
            queryset = Migrant.objects.all()
        if "lga_ids" in filters:
            queryset = queryset.filter(current_lga_id__in=filters["lga_ids"])
        if "status" in filters:
            queryset = queryset.filter(status=filters["status"])
        if "date_from" in filters:
            queryset = queryset.filter(created_at__gte=filters["date_from"])
        if "date_to" in filters:
            queryset = queryset.filter(created_at__lte=filters["date_to"])
        records = list(queryset.values())
        export.record_count = len(records)
        export_dir = f"{settings.MEDIA_ROOT}/exports"
        os.makedirs(export_dir, exist_ok=True)
        filename = f"export_{export.id}.{export.export_format}"
        filepath = f"{export_dir}/{filename}"
        if export.export_format == "csv":
            _write_csv(records, filepath)
        elif export.export_format == "json":
            _write_json(records, filepath)
        elif export.export_format == "excel":
            _write_excel(records, filepath)
        elif export.export_format == "geojson":
            _write_geojson(records, filepath)
        elif export.export_format == "ipfs":
            _write_json(records, filepath)
            ipfs_result = publish_to_ipfs(filepath)
            if ipfs_result.get("Hash"):
                export.ipfs_hash = ipfs_result["Hash"]
                export.ipfs_url = "https://ipfs.io/ipfs/" + ipfs_result["Hash"]
        export.file_path = filepath
        export.file_size = os.path.getsize(filepath)
        export.status = "completed"
        export.completed_at = timezone.now()
        export.save()
        return {
            "status": "completed",
            "export_id": str(export_id),
            "records": len(records),
            "file": filepath
        }
    except Exception as e:
        export.status = "failed"
        export.error_message = str(e)[:1000]
        export.save(update_fields=["status", "error_message"])
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=300)
        return {"status": "failed", "error": str(e)}

def _write_csv(records, filepath):
    if not records:
        with open(filepath, "w", newline="") as f:
            f.write("")
        return
    keys = records[0].keys()
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)

def _write_json(records, filepath):
    with open(filepath, "w") as f:
        json.dump(records, f, indent=2, default=str)

def _write_excel(records, filepath):
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        if records:
            ws.append(list(records[0].keys()))
            for r in records:
                ws.append([str(v) for v in r.values()])
        wb.save(filepath)
    except ImportError:
        _write_csv(records, filepath.replace(".xlsx", ".csv"))

def _write_geojson(records, filepath):
    features = []
    for r in records:
        feature = {
            "type": "Feature",
            "properties": {k: v for k, v in r.items() if k not in ["latitude", "longitude"]},
            "geometry": {
                "type": "Point",
                "coordinates": [r.get("longitude"), r.get("latitude")] if "longitude" in r and "latitude" in r else [0, 0]
            }
        }
        features.append(feature)
    geojson = {"type": "FeatureCollection", "features": features}
    with open(filepath, "w") as f:
        json.dump(geojson, f, indent=2)

def publish_to_ipfs(filepath):
    try:
        with open(filepath, "rb") as f:
            resp = requests.post("http://localhost:5001/api/v0/add", files={"file": f}, timeout=60)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    pinata_api = getattr(settings, "PINATA_API_KEY", None)
    pinata_secret = getattr(settings, "PINATA_SECRET_KEY", None)
    if pinata_api and pinata_secret:
        try:
            with open(filepath, "rb") as f:
                resp = requests.post(
                    "https://api.pinata.cloud/pinning/pinFileToIPFS",
                    headers={"pinata_api_key": pinata_api, "pinata_secret_api_key": pinata_secret},
                    files={"file": f},
                    timeout=120
                )
            if resp.status_code == 200:
                return {"Hash": resp.json().get("IpfsHash")}
        except Exception:
            pass
    return {"error": "IPFS not available"}
