from django.urls import path
from .views import offline_dashboard, sync_offline_data, service_worker, manifest

urlpatterns = [
    path("dashboard/", offline_dashboard, name="pwa-dashboard"),
    path("sync/", sync_offline_data, name="pwa-sync"),
    path("sw.js", service_worker, name="pwa-sw"),
    path("manifest.json", manifest, name="pwa-manifest"),
]