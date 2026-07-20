from rest_framework import serializers
from .models import NCFRMIMonthlyReport, NCFRMISubmissionLog

class NCFRMIMonthlyReportSerializer(serializers.ModelSerializer):
    prepared_by_name = serializers.CharField(source="prepared_by.get_full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)
    class Meta:
        model = NCFRMIMonthlyReport
        fields = ["id", "report_month", "report_year", "title", "summary",
                  "total_migrants_registered", "total_cases_opened", "total_cases_resolved",
                  "total_referrals_made", "total_referrals_completed", "returnees_assisted",
                  "vulnerable_cases_identified", "protection_incidents", "hotspot_alerts_issued",
                  "lga_breakdown", "challenges", "recommendations", "status",
                  "submitted_to_ncfrmi_at", "ncfrmi_reference", "prepared_by", "prepared_by_name",
                  "approved_by", "approved_by_name", "created_at", "updated_at"]

class NCFRMISubmissionLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source="performed_by.get_full_name", read_only=True)
    class Meta:
        model = NCFRMISubmissionLog
        fields = ["id", "report", "action", "notes", "performed_by", "performed_by_name", "created_at"]