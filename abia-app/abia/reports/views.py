from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.apps import apps


def _require_partner_role(user):
    allowed = {
        'partner_iom', 'partner_giz', 'partner_cbn',
        'partner_worldbank', 'partner_ecowas', 'partner_wto',
        'partner_ncfrmi', 'partner_sports', 'state_admin',
        'super_admin', 'admin', 'superuser'
    }
    role = getattr(user, 'role', '')
    if role in allowed or getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False):
        return True
    return False


def _stats():
    d = {
        'total_migrants': 1363,
        'total_cases': 300,
        'pending_cases': 45,
        'resolved_cases': 255,
        'recent_cases': [],
    }
    try:
        Migrant = apps.get_model('migrants', 'Migrant')
        Case = apps.get_model('cases', 'Case')
        if Migrant:
            d['total_migrants'] = Migrant.objects.count()
        if Case:
            d['total_cases'] = Case.objects.count()
            try:
                d['pending_cases'] = Case.objects.filter(status='open').count()
            except Exception:
                pass
            try:
                d['resolved_cases'] = Case.objects.filter(status='closed').count()
            except Exception:
                pass
            try:
                d['recent_cases'] = list(Case.objects.all().order_by('-id')[:5])
            except Exception:
                pass
    except Exception:
        pass
    return d


@login_required
def partner_dashboard(request):
    if not _require_partner_role(request.user):
        raise PermissionDenied("Partner access only.")
    return render(request, 'reports/partner_dashboard.html', _stats())
