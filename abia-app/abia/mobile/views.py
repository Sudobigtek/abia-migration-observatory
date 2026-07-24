from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.hotspot.models import HotspotPrediction
from abia.accounts.models import LGA


@login_required
def mobile_migrant_register(request):
    if request.method == "POST":
        try:
            migrant = Migrant.objects.create(
                first_name=request.POST.get("first_name"),
                last_name=request.POST.get("last_name"),
                phone_number=request.POST.get("phone_number"),
                email=request.POST.get("email") or "",
                date_of_birth=request.POST.get("date_of_birth") or None,
                gender=request.POST.get("gender"),
                current_lga_id=request.POST.get("current_lga"),
                origin_lga_id=request.POST.get("origin_lga") or None,
                migration_type=request.POST.get("migration_type"),
                is_vulnerable=request.POST.get("is_vulnerable") == "on",
                vulnerability_notes=request.POST.get("vulnerability_notes") or "",
                registered_by=request.user,
                gps_latitude=request.POST.get("gps_latitude") or None,
                gps_longitude=request.POST.get("gps_longitude") or None,
            )
            return JsonResponse({"status": "success", "migrant_id": migrant.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    lgas = LGA.objects.all().order_by("name")
    return render(request, "mobile/migrant_register.html", {"lgas": lgas})


@login_required
def mobile_case_open(request):
    if request.method == "POST":
        try:
            case = Case.objects.create(
                title=request.POST.get("title"),
                description=request.POST.get("description"),
                migrant_id=request.POST.get("migrant_id"),
                case_type=request.POST.get("case_type"),
                priority=request.POST.get("priority", "medium"),
                assigned_to_id=request.POST.get("assigned_to") or request.user.id,
                opened_by=request.user,
                lga_id=request.POST.get("lga"),
            )
            return JsonResponse({"status": "success", "case_id": case.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    lgas = LGA.objects.all().order_by("name")
    migrants = Migrant.objects.filter(registered_by=request.user).order_by("-created_at")[:50]
    return render(request, "mobile/case_open.html", {"lgas": lgas, "migrants": migrants})


@login_required
def mobile_dashboard(request):
    context = {
        "my_migrants": Migrant.objects.filter(registered_by=request.user).count(),
        "my_cases": Case.objects.filter(assigned_to=request.user).count(),
        "open_cases": Case.objects.filter(assigned_to=request.user, status="open").count(),
        "critical_hotspots": HotspotPrediction.objects.filter(risk_level="critical").count(),
    }
    return render(request, "mobile/dashboard.html", context)
