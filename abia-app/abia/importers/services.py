import csv
import io
import json
from datetime import datetime
from .models import ImportJob

class ImportService:
    @staticmethod
    def parse_csv(file_obj):
        decoded = file_obj.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))
        return list(reader)

    @staticmethod
    def import_migrants(rows, job):
        from abia.migrants.models import Migrant
        from accounts.models import LGA
        success = 0
        failed = 0
        errors = []
        for idx, row in enumerate(rows, 1):
            try:
                lga = None
                lga_name = row.get("current_lga", "")
                if lga_name:
                    lga = LGA.objects.filter(name__iexact=lga_name).first()
                Migrant.objects.create(
                    full_name=row.get("full_name", "").strip(),
                    phone=row.get("phone", "").strip() or None,
                    email=row.get("email", "").strip() or None,
                    gender=row.get("gender", "").strip() or None,
                    current_lga=lga,
                    status=row.get("status", "active").strip() or "active",
                    data_source="csv_import",
                )
                success += 1
            except Exception as e:
                failed += 1
                errors.append({"row": idx, "error": str(e)[:200]})
        job.success_rows = success
        job.failed_rows = failed
        job.error_log = errors
        job.status = "completed" if failed == 0 else "partial"
        if failed == len(rows):
            job.status = "failed"
        job.completed_at = datetime.now()
        job.save()
        return {"success": success, "failed": failed, "errors": errors}

    @staticmethod
    def import_cases(rows, job):
        from abia.cases.models import Case
        from accounts.models import LGA
        success = 0
        failed = 0
        errors = []
        for idx, row in enumerate(rows, 1):
            try:
                lga = None
                lga_name = row.get("current_lga", "")
                if lga_name:
                    lga = LGA.objects.filter(name__iexact=lga_name).first()
                Case.objects.create(
                    case_type=row.get("case_type", "general").strip(),
                    description=row.get("description", "").strip(),
                    status=row.get("status", "open").strip() or "open",
                    priority=row.get("priority", "medium").strip() or "medium",
                    current_lga=lga,
                    data_source="csv_import",
                )
                success += 1
            except Exception as e:
                failed += 1
                errors.append({"row": idx, "error": str(e)[:200]})
        job.success_rows = success
        job.failed_rows = failed
        job.error_log = errors
        job.status = "completed" if failed == 0 else "partial"
        if failed == len(rows):
            job.status = "failed"
        job.completed_at = datetime.now()
        job.save()
        return {"success": success, "failed": failed, "errors": errors}

    @staticmethod
    def process_import(job, file_obj):
        rows = ImportService.parse_csv(file_obj)
        job.total_rows = len(rows)
        job.processed_rows = len(rows)
        job.status = "processing"
        job.save()
        if job.entity_type == "migrants":
            return ImportService.import_migrants(rows, job)
        elif job.entity_type == "cases":
            return ImportService.import_cases(rows, job)
        job.status = "failed"
        job.error_log = [{"error": "Unknown entity type"}]
        job.save()
        return {"error": "Unknown entity type"}