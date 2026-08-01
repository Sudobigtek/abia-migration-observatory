from django.http import JsonResponse
from django.shortcuts import render
from django.apps import apps

def _get_count(app_label, model_name):
    try:
        Model = apps.get_model(app_label, model_name)
        return Model.objects.count()
    except Exception:
        return 0

def _get_list(app_label, model_name, limit=50):
    try:
        Model = apps.get_model(app_label, model_name)
        return list(Model.objects.all().values()[:limit])
    except Exception:
        return []

def _get_fields(app_label, model_name):
    try:
        Model = apps.get_model(app_label, model_name)
        return [f.name for f in Model._meta.fields]
    except Exception:
        return []

def migrant_list(request):
    count = _get_count('migrants', 'Migrant')
    data = _get_list('migrants', 'Migrant')
    fields = _get_fields('migrants', 'Migrant')
    
    if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
        return JsonResponse({"endpoint": "migrants", "count": count, "status": "ok", "results": data})
    
    return render(request, 'public_dashboard/data_table.html', {
        'title': 'Migrants Database',
        'endpoint': 'migrants',
        'count': count,
        'fields': fields,
        'data': data,
        'color': 'primary',
        'icon': 'bi-people-fill',
    })

def case_list(request):
    count = _get_count('cases', 'Case')
    data = _get_list('cases', 'Case')
    fields = _get_fields('cases', 'Case')
    
    if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
        return JsonResponse({"endpoint": "cases", "count": count, "status": "ok", "results": data})
    
    return render(request, 'public_dashboard/data_table.html', {
        'title': 'Cases & Interventions',
        'endpoint': 'cases',
        'count': count,
        'fields': fields,
        'data': data,
        'color': 'warning',
        'icon': 'bi-folder-fill',
    })

def referral_list(request):
    count = _get_count('referrals', 'Referral')
    data = _get_list('referrals', 'Referral')
    fields = _get_fields('referrals', 'Referral')
    
    if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
        return JsonResponse({"endpoint": "referrals", "count": count, "status": "ok", "results": data})
    
    return render(request, 'public_dashboard/data_table.html', {
        'title': 'Referrals & Transfers',
        'endpoint': 'referrals',
        'count': count,
        'fields': fields,
        'data': data,
        'color': 'info',
        'icon': 'bi-arrow-left-right',
    })
