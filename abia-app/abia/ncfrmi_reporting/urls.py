from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NCFRMIMonthlyReportViewSet, NCFRMISubmissionLogViewSet, generate_monthly, submit_report, approve_report, report_stats

router = DefaultRouter()
router.register(r"reports", NCFRMIMonthlyReportViewSet, basename="ncfrmireport")
router.register(r"logs", NCFRMISubmissionLogViewSet, basename="ncfrmlog")

urlpatterns = [
    path("", include(router.urls)),
    path("generate-monthly/", generate_monthly, name="ncfrmi-generate"),
    path("submit/<uuid:report_id>/", submit_report, name="ncfrmi-submit"),
    path("approve/<uuid:report_id>/", approve_report, name="ncfrmi-approve"),
    path("stats/", report_stats, name="ncfrmi-stats"),
]