from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from abia.ncfrmi_reporting.services import NCFRMIReportingService
from abia.ncfrmi_reporting.models import NCFRMIMonthlyReport

@login_required
def report_list(request):
    ncfrmi_reports = NCFRMIMonthlyReport.objects.all().order_by('-report_year', '-report_month')
    return render(request, 'reports/report_list.html', {
        'ncfrmi_reports': ncfrmi_reports,
        'giz_reports': [],
    })

@login_required
def ncfrmi_report_detail(request, pk):
    report = get_object_or_404(NCFRMIMonthlyReport, pk=pk)
    return render(request, 'ncfrmi/monthly_report.html', {'report': report})

@login_required
def ncfrmi_generate(request):
    from django.utils import timezone
    now = timezone.now()
    report = NCFRMIReportingService.generate_monthly_report(
        month=now.month, year=now.year, prepared_by=request.user
    )
    return render(request, 'ncfrmi/monthly_report.html', {'report': report})

@login_required
def ncfrmi_submit(request, pk):
    report = get_object_or_404(NCFRMIMonthlyReport, pk=pk)
    NCFRMIReportingService.submit_to_ncfrmi(report.id, request.user)
    return render(request, 'ncfrmi/monthly_report.html', {'report': report})
