"""
ABIA Migration Observatory — Cases API URLs
"""

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .search import search_cases

from abia.cases.views import CaseViewSet

router = DefaultRouter()
router.register(r"cases", CaseViewSet, basename="case")

urlpatterns = [
    path("", include(router.urls)),
    path("search/", search_cases, name="case-search"),
]