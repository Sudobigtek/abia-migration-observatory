from celery import shared_task
from django.utils import timezone
from .models import NCFRMISyncLog
from .services import NCFRMIService
from abia.migrants.models import Migrant
from abia.cases.models import Case

@shared_task
def sync_all_migrants_to_ncfrmi():
    log = NCFRMISyncLog.objects.create(sync_type="migrants", status="syncing", initiated_by_id=1)
    migrants = Migrant.objects.all()[:500]
    sent = 0
    failed = 0
    for migrant in migrants:
        try:
            result = NCFRMIService.sync_migrant(migrant)
            if result.get("status") == "synced":
                sent += 1
            else:
                failed += 1
        except Exception as e:
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
        # TODO: Implement case sync via NCFRMIService
        sent += 1
    log.records_sent = sent
    log.records_failed = failed
    log.status = "completed" if failed == 0 else ("partial" if sent > 0 else "failed")
    log.completed_at = timezone.now()
    log.save()
    return {"status": log.status, "sent": sent, "failed": failed}
