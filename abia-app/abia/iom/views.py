from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from abia.iom.services import IOMService


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
    from abia.iom.models import IOMReport
    report = get_object_or_404(IOMReport, pk=pk)
    IOMService.submit_to_iom(report.id, request.user)
    return render(request, "iom/migration_management_report.html", {"report": report})


# === LEGACY DRF VIEWSETS (required by urls.py) ===
from rest_framework import viewsets
from .models import IOMDataExchange, IOMIndicator
from .serializers import IOMDataExchangeSerializer, IOMIndicatorSerializer


class IOMDataExchangeViewSet(viewsets.ModelViewSet):
    queryset = IOMDataExchange.objects.all()
    serializer_class = IOMDataExchangeSerializer


class IOMIndicatorViewSet(viewsets.ModelViewSet):
    queryset = IOMIndicator.objects.all()
    serializer_class = IOMIndicatorSerializer


def iom_reports_api(request):
    return JsonResponse({"status": "ok", "count": IOMDataExchange.objects.count()})
