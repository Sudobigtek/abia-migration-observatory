from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebhookEndpointViewSet, WebhookDeliveryViewSet

router = DefaultRouter()
router.register(r'endpoints', WebhookEndpointViewSet, basename='webhookendpoint')
router.register(r'deliveries', WebhookDeliveryViewSet, basename='webhookdelivery')

urlpatterns = [path('', include(router.urls))]
