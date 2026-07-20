from django.db.models import Sum, Count
from django.utils import timezone
from .models import NCFRMIMonthlyReport, NCFRMISubmissionLog

class NCFRMIReportingService:
    @staticmethod
    def generate_monthly_report(month, year, prepared_by):
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        from abia.referrals.models import Referral
        from abia.hotspot.models import HotspotPrediction

        existing = NCFRMIMonthlyReport.objects.filter(report_month=month, report_year=year, prepared_by=prepared_by).first()
        if existing:
            return existing

        lga_data = list(Migrant.objects.values("current_lga__name").annotate(count=Count("id")).order_by("-count")[:20])

        report = NCFRMIMonthlyReport.objects.create(
            report_month=month,
            report_year=year,
            title=f"Abia State Migration Report - {month}/{year}",
            summary=f"Automated monthly report for Abia State Migration Observatory covering {month}/{year}.",
            total_migrants_registered=Migrant.objects.count(),
            total_cases_opened=Case.objects.count(),
            total_cases_resolved=Case.objects.filter(status="resolved").count(),
            total_referrals_made=Referral.objects.count(),
            total_referrals_completed=Referral.objects.filter(status="completed").count(),
            returnees_assisted=Migrant.objects.filter(status="returnee").count(),
            vulnerable_cases_identified=Case.objects.filter(priority="critical").count(),
            protection_incidents=Case.objects.filter(case_type__in=["trafficking", "gbv", "child_protection"]).count(),
            hotspot_alerts_issued=HotspotPrediction.objects.filter(risk_level="critical").count(),
            lga_breakdown=lga_data,
            prepared_by=prepared_by,
        )
        return report

    @staticmethod
    def submit_to_ncfrmi(report_id, user):
        report = NCFRMIMonthlyReport.objects.get(id=report_id)
        report.status = "submitted"
        report.submitted_to_ncfrmi_at = timezone.now()
        report.save()
        NCFRMISubmissionLog.objects.create(report=report, action="submitted_to_ncfrmi", performed_by=user)
        return report

    @staticmethod
    def approve_report(report_id, approver):
        report = NCFRMIMonthlyReport.objects.get(id=report_id)
        report.status = "approved"
        report.approved_by = approver
        report.save()
        NCFRMISubmissionLog.objects.create(report=report, action="approved_by_state", performed_by=approver)
        return report