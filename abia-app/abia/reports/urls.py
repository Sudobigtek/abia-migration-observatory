from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportTemplateViewSet, GeneratedReportViewSet, generate_report, report_types

router = DefaultRouter()
router.register(r"templates", ReportTemplateViewSet, basename="reporttemplate")
router.register(r"generated", GeneratedReportViewSet, basename="generatedreport")

urlpatterns = [
    path("", include(router.urls)),
    path("generate/", generate_report, name="reports-generate"),
    path("types/", report_types, name="reports-types"),
]