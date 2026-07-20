from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationPreferenceViewSet, mark_read, unread_count, broadcast

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"preferences", NotificationPreferenceViewSet, basename="notificationpref")

urlpatterns = [
    path("", include(router.urls)),
    path("mark-read/<uuid:notification_id>/", mark_read, name="notif-mark-read"),
    path("unread-count/", unread_count, name="notif-unread-count"),
    path("broadcast/", broadcast, name="notif-broadcast"),
]