import pytest
from abia.ncfrmi_reporting.models import NCFRMIMonthlyReport, NCFRMISubmissionLog
from abia.ncfrmi_reporting.repositories import NCFRMIMonthlyReportRepository, NCFRMISubmissionLogRepository

@pytest.mark.django_db
class TestNCFRMIMonthlyReportRepository:
    def test_get_by_month_year_preparer_returns_none_when_missing(self, db, admin_user):
        result = NCFRMIMonthlyReportRepository.get_by_month_year_preparer(1, 2026, admin_user)
        assert result is None

    def test_create_and_retrieve(self, db, admin_user):
        report = NCFRMIMonthlyReportRepository.create(
            report_month=7, report_year=2026, title="Test Report",
            summary="Test", prepared_by=admin_user
        )
        fetched = NCFRMIMonthlyReportRepository.get_by_id(report.id)
        assert fetched.title == "Test Report"

@pytest.mark.django_db
class TestNCFRMISubmissionLogRepository:
    def test_create_log(self, db, admin_user):
        report = NCFRMIMonthlyReport.objects.create(
            report_month=7, report_year=2026, title="Test",
            summary="Test", prepared_by=admin_user
        )
        log = NCFRMISubmissionLogRepository.create(
            report=report, action="test_action", performed_by=admin_user
        )
        assert log.action == "test_action"

    def test_log_is_linked_to_report(self, db, admin_user):
        report = NCFRMIMonthlyReport.objects.create(
            report_month=7, report_year=2026, title="Test",
            summary="Test", prepared_by=admin_user
        )
        NCFRMISubmissionLogRepository.create(report=report, action="submit")
        assert report.submission_logs.count() >= 1
