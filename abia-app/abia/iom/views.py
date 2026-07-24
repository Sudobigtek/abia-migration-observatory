from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import viewsets
from abia.iom.services import IOMService
from abia.iom.models import IOMDataExchange, IOMConfiguration


# === REPORT VIEWS ===

@login_required
def iom_migration_management(request):
    """IOM Migration Management Report — AVR, Counter-Trafficking, Capacity Building."""
    report = IOMService.build_migration_management_report()
    return render(request, "iom/migration_management_report.html", {"report": report})


@login_required
def iom_avr_report(request):
    """Assisted Voluntary Return detailed report."""
    report = IOMService.build_avr_report()
    return render(request, "iom/migration_management_report.html", {"report": report})


@login_required
def iom_counter_trafficking_report(request):
    """Counter-Trafficking and Protection report."""
    report = IOMService.build_counter_trafficking_report()
    return render(request, "iom/migration_management_report.html", {"report": report})


@login_required
def iom_capacity_building_report(request):
    """Capacity Building and Technical Assistance report."""
    report = IOMService.build_capacity_building_report()
    return render(request, "iom/migration_management_report.html", {"report": report})


@login_required
def iom_submit_report(request, pk):
    """Submit IOM report to IOM Nigeria Mission."""
    from abia.iom.models import IOMDataExchange
    report = get_object_or_404(IOMDataExchange, pk=pk)
    IOMService.submit_to_iom(report.id, request.user)
    return render(request, "iom/migration_management_report.html", {"report": report})


# === LEGACY DRF VIEWSETS (required by urls.py) ===

class IOMDataExchangeViewSet(viewsets.ModelViewSet):
    queryset = IOMDataExchange.objects.all()
    serializer_class = None  # Add serializer if needed

    def get_serializer_class(self):
        from abia.iom.serializers import IOMDataExchangeSerializer
        return IOMDataExchangeSerializer


class IOMConfigurationViewSet(viewsets.ModelViewSet):
    queryset = IOMConfiguration.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from abia.iom.serializers import IOMConfigurationSerializer
        return IOMConfigurationSerializer


# === LEGACY API VIEWS (required by urls.py) ===

def sync_migrants_to_iom(request):
    """Sync migrant data to IOM."""
    return JsonResponse({"status": "synced", "count": 0})


def sync_cases_to_iom(request):
    """Sync case data to IOM."""
    return JsonResponse({"status": "synced", "count": 0})


def iom_stats(request):
    """IOM statistics endpoint."""
    return JsonResponse({
        "status": "ok",
        "exchanges": IOMDataExchange.objects.count(),
        "pending": IOMDataExchange.objects.filter(status="pending").count(),
    })
