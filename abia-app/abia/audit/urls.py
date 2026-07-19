from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, ComplianceReportViewSet, generate_report

router = DefaultRouter()
router.register(r"logs", AuditLogViewSet, basename="auditlog")
router.register(r"reports", ComplianceReportViewSet, basename="compliancereport")

urlpatterns = [
    path("", include(router.urls)),
    path("generate-report/", generate_report, name="audit-generate-report"),
]