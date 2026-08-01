from django.http import JsonResponse
from django.shortcuts import render
from django.apps import apps

def _get_count(app_label, model_name):
    try:
        Model = apps.get_model(app_label, model_name)
        return Model.objects.count()
    except Exception:
        return 0

def _get_table_data(app_label, model_name, limit=50):
    try:
        Model = apps.get_model(app_label, model_name)
        fields = [f.name for f in Model._meta.fields][:8]
        queryset = list(Model.objects.all().values(*fields)[:limit])
        # Convert to rows aligned with fields
        rows = []
        for item in queryset:
            row = [str(item.get(f, '') or '—')[:30] for f in fields]
            rows.append(row)
        return fields, rows
    except Exception:
        return [], []

def migrant_list(request):
    count = _get_count('migrants', 'Migrant')
    fields, rows = _get_table_data('migrants', 'Migrant')
    if request.GET.get('format') == 'json':
        return JsonResponse({"endpoint": "migrants", "count": count, "status": "ok"})
    return render(request, 'public_dashboard/data_table.html', {
        'title': 'Migrants Database', 'endpoint': 'migrants', 'count': count,
        'fields': fields, 'rows': rows, 'color': 'primary', 'icon': 'bi-people-fill',
    })

def case_list(request):
    count = _get_count('cases', 'Case')
    fields, rows = _get_table_data('cases', 'Case')
    if request.GET.get('format') == 'json':
        return JsonResponse({"endpoint": "cases", "count": count, "status": "ok"})
    return render(request, 'public_dashboard/data_table.html', {
        'title': 'Cases & Interventions', 'endpoint': 'cases', 'count': count,
        'fields': fields, 'rows': rows, 'color': 'warning', 'icon': 'bi-folder-fill',
    })

def referral_list(request):
    count = _get_count('referrals', 'Referral')
    fields, rows = _get_table_data('referrals', 'Referral')
    if request.GET.get('format') == 'json':
        return JsonResponse({"endpoint": "referrals", "count": count, "status": "ok"})
    return render(request, 'public_dashboard/data_table.html', {
        'title': 'Referrals & Transfers', 'endpoint': 'referrals', 'count': count,
        'fields': fields, 'rows': rows, 'color': 'info', 'icon': 'bi-arrow-left-right',
    })
