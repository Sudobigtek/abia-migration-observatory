from celery import shared_task
from django.utils import timezone
from .models import SMSCampaign, SMSLog
from .services import send_sms
from abia.migrants.models import Migrant

@shared_task
def execute_sms_campaign(campaign_id):
    try:
        campaign = SMSCampaign.objects.get(id=campaign_id)
    except SMSCampaign.DoesNotExist:
        return {"status": "not_found"}
    if campaign.status != "scheduled":
        return {"status": "invalid_status", "current": campaign.status}
    campaign.status = "sending"
    campaign.save(update_fields=["status"])
    recipients = Migrant.objects.filter(phone__isnull=False).exclude(phone="")
    if campaign.target_lgas.exists():
        recipients = recipients.filter(current_lga__in=campaign.target_lgas.all())
    if campaign.target_status:
        recipients = recipients.filter(status=campaign.target_status)
    campaign.total_recipients = recipients.count()
    campaign.save(update_fields=["total_recipients"])
    sent = 0
    failed = 0
    for migrant in recipients.iterator():
        result = send_sms(migrant.phone, campaign.message, provider=campaign.provider)
        log = SMSLog.objects.create(
            campaign=campaign,
            recipient=migrant,
            phone=migrant.phone,
            message=campaign.message,
            status="sent" if result["status"] == "sent" else "failed",
            provider_response=result,
            error_message=result.get("error", ""),
            sent_at=timezone.now() if result["status"] == "sent" else None
        )
        if result["status"] == "sent":
            sent += 1
        else:
            failed += 1
    campaign.sent_count = sent
    campaign.failed_count = failed
    campaign.status = "completed" if failed == 0 else ("failed" if sent == 0 else "completed")
    campaign.sent_at = timezone.now()
    campaign.save()
    return {
        "status": "completed",
        "campaign_id": str(campaign_id),
        "total": campaign.total_recipients,
        "sent": sent,
        "failed": failed
    }

@shared_task
def send_individual_sms(migrant_id, message, campaign_id=None):
    try:
        migrant = Migrant.objects.get(id=migrant_id)
    except Migrant.DoesNotExist:
        return {"status": "not_found"}
    if not migrant.phone:
        return {"status": "no_phone"}
    result = send_sms(migrant.phone, message)
    SMSLog.objects.create(
        campaign_id=campaign_id,
        recipient=migrant,
        phone=migrant.phone,
        message=message,
        status="sent" if result["status"] == "sent" else "failed",
        provider_response=result,
        error_message=result.get("error", ""),
        sent_at=timezone.now() if result["status"] == "sent" else None
    )
    return result
