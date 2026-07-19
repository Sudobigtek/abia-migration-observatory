"""
ABIA Migration Observatory — Migrants API URLs
"""

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .search import search_migrants, search_migrants_simple
from .import_export import migrants_export, migrants_import

from abia.migrants.views import MigrantViewSet, MigrantVersionViewSet, PhotoUploadQueueViewSet

router = DefaultRouter()
router.register(r"migrants", MigrantViewSet, basename="migrant")
router.register(r"migrant-versions", MigrantVersionViewSet, basename="migrant-version")
router.register(r"photo-queue", PhotoUploadQueueViewSet, basename="photo-queue")

urlpatterns = [
    path("", include(router.urls)),
]