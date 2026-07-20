from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AthleteProfileViewSet, AthleteTransferViewSet, SportsConfigurationViewSet, transfers_by_destination, talent_export_value, athletes_by_sport, top_valued_athletes, lga_talent_map

router = DefaultRouter()
router.register(r"athletes", AthleteProfileViewSet, basename="athlete")
router.register(r"transfers", AthleteTransferViewSet, basename="transfer")
router.register(r"config", SportsConfigurationViewSet, basename="sportsconfig")

urlpatterns = [
    path("", include(router.urls)),
    path("by-destination/", transfers_by_destination, name="sports-destinations"),
    path("export-value/", talent_export_value, name="sports-export-value"),
    path("by-sport/", athletes_by_sport, name="sports-by-sport"),
    path("top-valued/", top_valued_athletes, name="sports-top-valued"),
    path("lga-talent/", lga_talent_map, name="sports-lga-talent"),
]