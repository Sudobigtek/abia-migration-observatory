from django.http import JsonResponse
from django.apps import apps

def _get_count(app_label, model_name):
    try:
        Model = apps.get_model(app_label, model_name)
        return Model.objects.count()
    except Exception:
        return 0

def migrant_list(request):
    count = _get_count('migrants', 'Migrant')
    return JsonResponse({"endpoint": "migrants", "count": count, "status": "ok"})

def case_list(request):
    count = _get_count('cases', 'Case')
    return JsonResponse({"endpoint": "cases", "count": count, "status": "ok"})

def referral_list(request):
    count = _get_count('referrals', 'Referral')
    return JsonResponse({"endpoint": "referrals", "count": count, "status": "ok"})
