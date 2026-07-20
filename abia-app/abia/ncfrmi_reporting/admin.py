from django.contrib import admin
from .models import NCFRMIMonthlyReport, NCFRMISubmissionLog

@admin.register(NCFRMIMonthlyReport)
class NCFRMIMonthlyReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_month", "report_year", "status", "total_migrants_registered", "prepared_by", "created_at"]
    list_filter = ["status", "report_year", "report_month"]
    search_fields = ["title", "ncfrmi_reference"]

@admin.register(NCFRMISubmissionLog)
class NCFRMISubmissionLogAdmin(admin.ModelAdmin):
    list_display = ["report", "action", "performed_by", "created_at"]
    list_filter = ["action", "created_at"]