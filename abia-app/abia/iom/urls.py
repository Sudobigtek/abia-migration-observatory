from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IOMDataExchangeViewSet, IOMConfigurationViewSet, sync_migrants_to_iom, sync_cases_to_iom, iom_stats

router = DefaultRouter()
router.register(r"exchanges", IOMDataExchangeViewSet, basename="iomexchange")
router.register(r"config", IOMConfigurationViewSet, basename="iomconfig")

urlpatterns = [
    path("", include(router.urls)),
    path("sync-migrants/", sync_migrants_to_iom, name="iom-sync-migrants"),
    path("sync-cases/", sync_cases_to_iom, name="iom-sync-cases"),
    path("stats/", iom_stats, name="iom-stats"),
]