from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PushDeviceViewSet, PushNotificationViewSet

router = DefaultRouter()
router.register(r'devices', PushDeviceViewSet, basename='pushdevice')
router.register(r'notifications', PushNotificationViewSet, basename='pushnotification')

urlpatterns = [path('', include(router.urls))]
