from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataQualityRuleViewSet, DataQualityIssueViewSet, run_checks, quality_dashboard

router = DefaultRouter()
router.register(r"rules", DataQualityRuleViewSet, basename="qualityrule")
router.register(r"issues", DataQualityIssueViewSet, basename="qualityissue")

urlpatterns = [
    path("", include(router.urls)),
    path("run-checks/", run_checks, name="quality-run-checks"),
    path("dashboard/", quality_dashboard, name="quality-dashboard"),
]