from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from abia.giz.services import GIZService

@login_required
def giz_migration_governance(request):
    report = GIZService.build_migration_governance_report()
    return render(request, 'giz/migration_governance_report.html', {'report': report})

@login_required
def giz_reintegration(request):
    report = GIZService.build_reintegration_report()
    return render(request, 'giz/migration_governance_report.html', {'report': report})

@login_required
def giz_protection(request):
    report = GIZService.build_protection_report()
    return render(request, 'giz/migration_governance_report.html', {'report': report})

# === LEGACY DRF VIEWSETS (required by urls.py) ===
from rest_framework import viewsets
from .models import GIZDataExchange, GIZIndicator
from .serializers import GIZDataExchangeSerializer, GIZIndicatorSerializer

class GIZDataExchangeViewSet(viewsets.ModelViewSet):
    queryset = GIZDataExchange.objects.all()
    serializer_class = GIZDataExchangeSerializer

class GIZIndicatorViewSet(viewsets.ModelViewSet):
    queryset = GIZIndicator.objects.all()
    serializer_class = GIZIndicatorSerializer

def giz_reports(request):
    from django.http import JsonResponse
    return JsonResponse({"status": "ok", "count": GIZDataExchange.objects.count()})

def migration_governance_report(request):
    from django.http import JsonResponse
    return JsonResponse(GIZService.build_migration_governance_report())

def reintegration_report(request):
    from django.http import JsonResponse
    return JsonResponse(GIZService.build_reintegration_report())

def protection_report(request):
    from django.http import JsonResponse
    return JsonResponse(GIZService.build_protection_report())

def submit_report(request, pk):
    from django.http import JsonResponse
    GIZService.submit_to_giz(pk)
    return JsonResponse({"status": "submitted"})

def refresh_indicators(request):
    from django.http import JsonResponse
    return JsonResponse(GIZService.update_indicators_from_data())
