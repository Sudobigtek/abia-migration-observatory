from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

@login_required
def offline_dashboard(request):
    return render(request, "pwa/offline.html")

@csrf_exempt
@login_required
def sync_offline_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        payload = json.loads(request.body)
        records = payload.get("records", [])
        synced = 0
        failed = 0
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        for record in records:
            try:
                entity_type = record.get("entity_type")
                if entity_type == "migrant":
                    Migrant.objects.create(
                        full_name=record.get("full_name"),
                        phone=record.get("phone"),
                        data_source="offline_pwa",
                        status="active"
                    )
                elif entity_type == "case":
                    Case.objects.create(
                        case_type=record.get("case_type"),
                        description=record.get("description"),
                        status="open",
                        data_source="offline_pwa"
                    )
                synced += 1
            except Exception:
                failed += 1
        return JsonResponse({"synced": synced, "failed": failed, "total": len(records)})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

@login_required
def service_worker(request):
    return render(request, "pwa/sw.js", content_type="application/javascript")

@login_required
def manifest(request):
    return JsonResponse({
        "name": "Abia Migration Observatory",
        "short_name": "AbiaObs",
        "start_url": "/pwa/dashboard/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1a5f7a",
        "icons": [{"src": "/static/icon-192.png", "sizes": "192x192"}]
    })