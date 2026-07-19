from .models import AuditLog
from django.utils import timezone
import django.db.models as models

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

def log_action(user, action, entity_type, entity_id=None, entity_repr="",
             old_values=None, new_values=None, request=None, reason=""):
    ip_address = None
    user_agent = ""
    session_id = ""
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:1000]
        session_id = request.session.session_key or ""
    AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else "",
        entity_repr=entity_repr[:255],
        old_values=old_values or {},
        new_values=new_values or {},
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id,
        reason=reason
    )

def generate_compliance_report(period_start, period_end, report_type="ad_hoc"):
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    from abia.referrals.models import Referral
    data = {
        "period": {"start": str(period_start), "end": str(period_end)},
        "migrants_registered": Migrant.objects.filter(created_at__date__range=[period_start, period_end]).count(),
        "cases_opened": Case.objects.filter(created_at__date__range=[period_start, period_end]).count(),
        "cases_resolved": Case.objects.filter(status="resolved", updated_at__date__range=[period_start, period_end]).count(),
        "referrals_made": Referral.objects.filter(created_at__date__range=[period_start, period_end]).count(),
        "audit_events": list(AuditLog.objects.filter(created_at__date__range=[period_start, period_end]).values("action").annotate(count=models.Count("id")).values("action", "count")),
    }
    return data