from django.urls import path
from .views import (
    geo_lga_boundaries, geo_lga_detail, geo_hotspots,
    geo_hotspots_list, geo_heatmap_data, geo_nearby
)

urlpatterns = [
    path('lga-boundaries/', geo_lga_boundaries, name='geo-lga-boundaries'),
    path('lga-boundaries/<uuid:lga_id>/', geo_lga_detail, name='geo-lga-detail'),
    path('hotspots/', geo_hotspots, name='geo-hotspots'),
    path('hotspots/list/', geo_hotspots_list, name='geo-hotspots-list'),
    path('heatmap/', geo_heatmap_data, name='geo-heatmap'),
    path('nearby/', geo_nearby, name='geo-nearby'),
]
