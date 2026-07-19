from django.urls import path
from .views import map_data, trigger_analysis, hotspot_list

urlpatterns = [
    path("map-data/", map_data, name="hotspot-map-data"),
    path("trigger-analysis/", trigger_analysis, name="hotspot-trigger"),
    path("list/", hotspot_list, name="hotspot-list"),
]