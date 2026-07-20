from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WBIndicatorViewSet, WBDataPointViewSet, WBConfigurationViewSet, indicator_trend, migration_indicators, remittance_indicators

router = DefaultRouter()
router.register(r"indicators", WBIndicatorViewSet, basename="wbindicator")
router.register(r"data-points", WBDataPointViewSet, basename="wb datapoint")
router.register(r"config", WBConfigurationViewSet, basename="wbconfig")

urlpatterns = [
    path("", include(router.urls)),
    path("trend/<str:indicator_code>/", indicator_trend, name="wb-trend"),
    path("migration/", migration_indicators, name="wb-migration"),
    path("remittance/", remittance_indicators, name="wb-remittance"),
]