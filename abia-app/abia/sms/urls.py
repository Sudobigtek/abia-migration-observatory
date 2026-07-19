from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SMSCampaignViewSet, SMSLogViewSet, send_single_sms

router = DefaultRouter()
router.register(r"campaigns", SMSCampaignViewSet, basename="smscampaign")
router.register(r"logs", SMSLogViewSet, basename="smslog")

urlpatterns = [
    path("", include(router.urls)),
    path("send/", send_single_sms, name="sms-send-single"),
]
