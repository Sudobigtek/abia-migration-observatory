from django.db.models import Sum, Count
from django.utils import timezone
from .repositories import NCFRMIMonthlyReportRepository, NCFRMISubmissionLogRepository
from abia.migrants.repositories import MigrantRepository
from abia.cases.repositories import CaseRepository
from abia.referrals.repositories import ReferralRepository
from abia.hotspot.repositories import HotspotRepository

class NCFRMIReportingService:
    @staticmethod
    def generate_monthly_report(month, year, prepared_by):
        existing = NCFRMIMonthlyReportRepository.get_by_month_year_preparer(month, year, prepared_by)
        if existing:
            return existing

        lga_data = MigrantRepository.get_lga_breakdown(20)

        report = NCFRMIMonthlyReportRepository.create(
            report_month=month,
            report_year=year,
            title=f"Abia State Migration Report - {month}/{year}",
            summary=f"Automated monthly report for Abia State Migration Observatory covering {month}/{year}.",
            total_migrants_registered=MigrantRepository.count(),
            total_cases_opened=CaseRepository.count(),
            total_cases_resolved=CaseRepository.filter_count(status="resolved"),
            total_referrals_made=ReferralRepository.count(),
            total_referrals_completed=ReferralRepository.filter_count(status="completed"),
            returnees_assisted=MigrantRepository.filter_count(status="returnee"),
            vulnerable_cases_identified=CaseRepository.filter_count(priority="critical"),
            protection_incidents=CaseRepository.filter_count(case_type__in=["trafficking", "gbv", "child_protection"]),
            hotspot_alerts_issued=HotspotRepository.filter_count(risk_level="critical"),
            lga_breakdown=lga_data,
            prepared_by=prepared_by,
        )
        return report

    @staticmethod
    def submit_to_ncfrmi(report_id, user):
        report = NCFRMIMonthlyReportRepository.get_by_id(report_id)
        report.status = "submitted"
        report.submitted_to_ncfrmi_at = timezone.now()
        report.save()
        NCFRMISubmissionLogRepository.create(report=report, action="submitted_to_ncfrmi", performed_by=user)
        return report

    @staticmethod
    def approve_report(report_id, approver):
        report = NCFRMIMonthlyReportRepository.get_by_id(report_id)
        report.status = "approved"
        report.approved_by = approver
        report.save()
        NCFRMISubmissionLogRepository.create(report=report, action="approved_by_state", performed_by=approver)
        return report