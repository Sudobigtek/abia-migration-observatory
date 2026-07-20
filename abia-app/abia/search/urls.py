from django.urls import path
from .views import search, rebuild_index, search_facets

urlpatterns = [
    path("search/", search, name="search"),
    path("rebuild/", rebuild_index, name="search-rebuild"),
    path("facets/", search_facets, name="search-facets"),
]