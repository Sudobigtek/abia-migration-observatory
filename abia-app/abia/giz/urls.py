from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GIZDataExchangeViewSet, GIZIndicatorViewSet, giz_reports, migration_governance_report, reintegration_report, protection_report, submit_report, refresh_indicators

router = DefaultRouter()
router.register(r"exchanges", GIZDataExchangeViewSet, basename="gizexchange")
router.register(r"indicators", GIZIndicatorViewSet, basename="gizindicator")

urlpatterns = [
    path("", include(router.urls)),
    path("reports/", giz_reports, name="giz-reports"),
    path("reports/migration-governance/", migration_governance_report, name="giz-migration-report"),
    path("reports/reintegration/", reintegration_report, name="giz-reintegration-report"),
    path("reports/protection/", protection_report, name="giz-protection-report"),
    path("submit/<uuid:exchange_id>/", submit_report, name="giz-submit"),
    path("refresh-indicators/", refresh_indicators, name="giz-refresh"),
]