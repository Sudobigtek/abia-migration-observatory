from django.urls import path
from .views import global_search, search_reindex

urlpatterns = [
    path('', global_search, name='global-search'),
    path('reindex/', search_reindex, name='search-reindex'),
]
