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
