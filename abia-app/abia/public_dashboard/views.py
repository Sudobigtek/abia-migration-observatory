from django.shortcuts import render
from django.utils import timezone
from django.db import DatabaseError


class DashboardService:
    """
    Aggregates live counts from the migration observatory database.
    Falls back to zeros if tables are empty or models don't exist yet.
    """

    @staticmethod
    def get_counts():
        data = {
            "total_migrants": 0,
            "total_cases": 0,
            "active_cases": 0,
            "resolved_cases": 0,
            "pending_referrals": 0,
            "last_updated": timezone.now(),
        }

        try:
            from abia.migrants.models import Migrant
            data["total_migrants"] = Migrant.objects.count()
        except (ImportError, DatabaseError):
            pass

        try:
            from abia.cases.models import Case
            data["total_cases"] = Case.objects.count()
            # Adjust field names if your Case model uses different status values
            data["active_cases"] = Case.objects.filter(status="active").count()
            data["resolved_cases"] = Case.objects.filter(status="resolved").count()
        except (ImportError, DatabaseError):
            pass

        try:
            from abia.referrals.models import Referral
            data["pending_referrals"] = Referral.objects.filter(status="pending").count()
        except (ImportError, DatabaseError):
            pass

        return data


def public_dashboard(request):
    context = DashboardService.get_counts()
    return render(request, "public_dashboard/dashboard.html", context)


def public_map_data(request):
    """
    Returns geoJSON or simple JSON for the public migration map.
    Stub implementation — replace with actual map data query.
    """
    from django.http import JsonResponse
    return JsonResponse({
        "type": "FeatureCollection",
        "features": []
    })


def public_feedback(request):
    from django.http import JsonResponse
    return JsonResponse({"message": "Feedback endpoint — implement form handling"})

def feedback_success(request):
    from django.http import JsonResponse
    return JsonResponse({"message": "Feedback submitted successfully"})

def sdg_dashboard(request):
    from django.http import JsonResponse
    return JsonResponse({"message": "SDG-GCM Dashboard — implement SDG metrics"})

def migrant_register(request):
    from django.http import JsonResponse
    return JsonResponse({"message": "Migrant registration — implement form"})

def registration_success(request):
    from django.http import JsonResponse
    return JsonResponse({"message": "Registration successful"})

def status_check(request):
    from django.http import JsonResponse
    return JsonResponse({"message": "Status check — implement case status lookup"})
