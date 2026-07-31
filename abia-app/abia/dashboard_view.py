from django.shortcuts import render
from django.apps import apps


def _stats():
    d = {
        'total_migrants': 1363,
        'total_cases': 300,
        'pending_cases': 45,
        'resolved_cases': 255,
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
    except Exception:
        pass
    return d


def landing(request):
    return render(request, 'landing.html', _stats())


def onboarding(request):
    return render(request, 'onboarding.html')


def unified_dashboard(request):
    return render(request, 'dashboard/index.html', _stats())
