"""Notification Celery tasks."""

import requests
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@shared_task
def send_sms_alert(phone_number, message):
    """Send SMS via HTTPSMS API."""
    if not getattr(settings, "HTTPSMS_API_KEY", None):
        return {
            "status": "skipped",
            "reason": "HTTPSMS_API_KEY not configured",
        }

    resp = requests.post(
        "https://api.httpsms.com/v1/messages",
        headers={
            "Authorization": f"Bearer {settings.HTTPSMS_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "phone_number": phone_number,
            "content": message,
            "sender_id": getattr(settings, "HTTPSMS_SENDER_ID", "AbiaObs"),
        },
        timeout=30,
    )
    return {
        "status": "sent" if resp.status_code == 200 else "failed",
        "response": resp.text,
    }


@shared_task
def send_case_overdue_alert(case_id):
    """Notify case assignee when case is overdue."""
    from abia.cases.models import Case

    try:
        case = Case.objects.select_related("assigned_to").get(id=case_id)
    except Case.DoesNotExist:
        return

    if not case.assigned_to:
        return

    assignee = case.assigned_to
    msg = (
        f"[Abia Observatory] Case #{case.id} ({case.title}) "
        f"is OVERDUE. Priority: {case.priority}. Please update status."
    )

    if assignee.phone_number:
        send_sms_alert.delay(assignee.phone_number, msg)

    if assignee.email:
        send_mail(
            subject=f"Overdue Case Alert — #{case.id}",
            message=(
                f"Case #{case.id}: {case.title} is overdue.\n"
                f"Priority: {case.priority}\n"
                f"Please update status in the dashboard."
            ),
            from_email=getattr(
                settings,
                "DEFAULT_FROM_EMAIL",
                "alerts@abia-migration.gov.ng",
            ),
            recipient_list=[assignee.email],
            fail_silently=True,
        )


@shared_task
def send_hotspot_alert(hotspot_id):
    """Send critical hotspot alert to all field officers."""
    from abia.hotspot.models import HotspotAlert

    try:
        hotspot = HotspotAlert.objects.select_related("lga").get(
            id=hotspot_id
        )
    except HotspotAlert.DoesNotExist:
        return

    if hotspot.severity != "critical":
        return

    officers = User.objects.filter(
        role="field_officer", is_active=True
    )
    lga_name = hotspot.lga.name if hotspot.lga else "Unknown LGA"
    affected = hotspot.estimated_affected or "Unknown"

    msg = (
        f"[CRITICAL HOTSPOT] {hotspot.title} in {lga_name}. "
        f"Severity: CRITICAL. Affected: {affected}. "
        f"Check dashboard immediately."
    )

    for officer in officers:
        if officer.phone_number:
            send_sms_alert.delay(officer.phone_number, msg)


@shared_task
def send_daily_digest():
    """Send daily summary email to coordinators."""
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    from abia.referrals.models import Referral
    from abia.hotspot.models import HotspotAlert

    coordinators = User.objects.filter(
        role__in=["state_coordinator", "admin"], is_active=True
    )

    total_migrants = Migrant.objects.count()
    open_cases = Case.objects.filter(status="open").count()
    pending_refs = Referral.objects.filter(status="pending").count()
    active_hotspots = HotspotAlert.objects.filter(is_active=True).count()

    body = f"""Abia Migration Observatory — Daily Digest
Summary ({timezone.now().strftime("%Y-%m-%d")}):

Total Migrants Registered: {total_migrants}
Open Cases: {open_cases}
Pending Referrals: {pending_refs}
Active Hotspots: {active_hotspots}
View full dashboard: https://abia-migration.gov.ng/dashboard/
"""

    for coord in coordinators:
        if coord.email:
            send_mail(
                subject="Abia Observatory — Daily Digest",
                message=body,
                from_email=getattr(
                    settings,
                    "DEFAULT_FROM_EMAIL",
                    "alerts@abia-migration.gov.ng",
                ),
                recipient_list=[coord.email],
                fail_silently=True,
            )
