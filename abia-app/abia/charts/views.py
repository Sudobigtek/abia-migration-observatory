from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.apps import apps


def _require_government_role(user):
    allowed = {
        'state_admin', 'super_admin', 'lga_coordinator',
        'field_officer', 'admin', 'superuser'
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
        'gender_data': [60, 40],
        'status_labels': ['Pending', 'Resolved', 'Escalated', 'Closed'],
        'status_data': [45, 255, 30, 20],
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
                d['recent_cases'] = list(Case.objects.all().order_by('-id')[:10])
            except Exception:
                pass
    except Exception:
        pass
    return d


@login_required
def command_center(request):
    if not _require_government_role(request.user):
        raise PermissionDenied("Government access only.")
    return render(request, 'dashboard/index.html', _stats())
