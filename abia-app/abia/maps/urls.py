from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MapLayerViewSet, map_data, lga_boundaries, hotspot_map, map_config

router = DefaultRouter()
router.register(r"layers", MapLayerViewSet, basename="maplayer")

urlpatterns = [
    path("", include(router.urls)),
    path("data/", map_data, name="map-data"),
    path("boundaries/", lga_boundaries, name="map-boundaries"),
    path("hotspots/", hotspot_map, name="map-hotspots"),
    path("config/", map_config, name="map-config"),
]