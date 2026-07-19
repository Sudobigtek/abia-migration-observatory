"""
ABIA Migration Observatory — Referrals API URLs
"""

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from abia.referrals.views import ReferralViewSet

router = DefaultRouter()
router.register(r"referrals", ReferralViewSet, basename="referral")

urlpatterns = [
    path("", include(router.urls)),
]
