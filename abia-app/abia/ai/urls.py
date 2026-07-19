from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RiskAssessmentViewSet, ai_assess_migrant, ai_health

router = DefaultRouter()
router.register(r"risk-assessments", RiskAssessmentViewSet, basename="riskassessment")

urlpatterns = [
    path("", include(router.urls)),
    path("assess/<uuid:migrant_id>/", ai_assess_migrant, name="ai-assess-migrant"),
    path("health/", ai_health, name="ai-health"),
]
