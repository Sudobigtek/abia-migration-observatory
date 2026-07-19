"""
ABIA Migration Observatory — Accounts API URLs
"""

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from abia.accounts.views import LGAViewSet, UserViewSet

router = DefaultRouter()
router.register(r"lgas", LGAViewSet, basename="lga")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
