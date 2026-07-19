from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataQualityRuleViewSet, DataQualityIssueViewSet, quality_overview, run_quality_check

router = DefaultRouter()
router.register(r'rules', DataQualityRuleViewSet, basename='dataqualityrule')
router.register(r'issues', DataQualityIssueViewSet, basename='dataqualityissue')

urlpatterns = [
    path('', include(router.urls)),
    path('overview/', quality_overview, name='quality-overview'),
    path('scan/', run_quality_check, name='quality-scan'),
]
