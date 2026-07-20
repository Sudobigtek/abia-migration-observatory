from .models import NCFRMIMonthlyReport, NCFRMISubmissionLog

class NCFRMIMonthlyReportRepository:
    @staticmethod
    def get_by_month_year_preparer(month, year, prepared_by):
        return NCFRMIMonthlyReport.objects.filter(
            report_month=month, report_year=year, prepared_by=prepared_by
        ).first()

    @staticmethod
    def get_by_id(report_id):
        return NCFRMIMonthlyReport.objects.get(id=report_id)

    @staticmethod
    def create(**kwargs):
        return NCFRMIMonthlyReport.objects.create(**kwargs)

class NCFRMISubmissionLogRepository:
    @staticmethod
    def create(**kwargs):
        return NCFRMISubmissionLog.objects.create(**kwargs)