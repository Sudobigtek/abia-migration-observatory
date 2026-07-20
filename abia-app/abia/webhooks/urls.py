from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebhookEndpointViewSet, WebhookDeliveryViewSet, trigger_event, retry_failed, webhook_stats

router = DefaultRouter()
router.register(r"endpoints", WebhookEndpointViewSet, basename="webhookendpoint")
router.register(r"deliveries", WebhookDeliveryViewSet, basename="webhookdelivery")

urlpatterns = [
    path("", include(router.urls)),
    path("trigger/", trigger_event, name="webhooks-trigger"),
    path("retry/", retry_failed, name="webhooks-retry"),
    path("stats/", webhook_stats, name="webhooks-stats"),
]