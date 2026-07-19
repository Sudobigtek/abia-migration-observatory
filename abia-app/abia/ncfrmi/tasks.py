from celery import shared_task
from django.utils import timezone
from .models import NCFRMISyncLog, NCFRMIMigrantMapping
from .services import sync_migrant_to_ncfrmi, sync_case_to_ncfrmi
from abia.migrants.models import Migrant
from abia.cases.models import Case

@shared_task
def sync_all_migrants_to_ncfrmi():
    log = NCFRMISyncLog.objects.create(sync_type="migrants", status="syncing", initiated_by_id=1)
    migrants = Migrant.objects.filter(ncfrmi_mapping__isnull=True)[:500]
    sent = 0
    failed = 0
    for migrant in migrants:
        result = sync_migrant_to_ncfrmi(migrant)
        if result["status"] == "synced":
            mapping, _ = NCFRMIMigrantMapping.objects.get_or_create(local_migrant=migrant)
            mapping.ncfrmi_id = result.get("ncfrmi_id", "")
            mapping.last_synced_at = timezone.now()
            mapping.sync_status = "synced"
            mapping.save()
            sent += 1
        else:
            failed += 1
    log.records_sent = sent
    log.records_failed = failed
    log.status = "completed" if failed == 0 else ("partial" if sent > 0 else "failed")
    log.completed_at = timezone.now()
    log.save()
    return {"status": log.status, "sent": sent, "failed": failed}

@shared_task
def sync_all_cases_to_ncfrmi():
    log = NCFRMISyncLog.objects.create(sync_type="cases", status="syncing", initiated_by_id=1)
    cases = Case.objects.filter(data_source="abia_observatory")[:500]
    sent = 0
    failed = 0
    for case in cases:
        result = sync_case_to_ncfrmi(case)
        if result["status"] == "synced":
            sent += 1
        else:
            failed += 1
    log.records_sent = sent
    log.records_failed = failed
    log.status = "completed" if failed == 0 else ("partial" if sent > 0 else "failed")
    log.completed_at = timezone.now()
    log.save()
    return {"status": log.status, "sent": sent, "failed": failed}
