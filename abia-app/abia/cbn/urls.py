from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RemittanceRecordViewSet, CBNConfigurationViewSet, remittance_summary, remittance_by_lga, remittance_by_channel, remittance_trends

router = DefaultRouter()
router.register(r"records", RemittanceRecordViewSet, basename="remittance")
router.register(r"config", CBNConfigurationViewSet, basename="cbnconfig")

urlpatterns = [
    path("", include(router.urls)),
    path("summary/", remittance_summary, name="cbn-summary"),
    path("by-lga/", remittance_by_lga, name="cbn-by-lga"),
    path("by-channel/", remittance_by_channel, name="cbn-by-channel"),
    path("trends/", remittance_trends, name="cbn-trends"),
]