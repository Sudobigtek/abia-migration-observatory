from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportTemplateViewSet, GeneratedReportViewSet, report_dashboard

router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet, basename='reporttemplate')
router.register(r'generated', GeneratedReportViewSet, basename='generatedreport')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', report_dashboard, name='report-dashboard'),
]
