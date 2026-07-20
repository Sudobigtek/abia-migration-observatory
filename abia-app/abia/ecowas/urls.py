from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ECOWASMigrantFlowViewSet, ECOWASTradeFlowViewSet, ECOWASConfigurationViewSet, migration_corridors, migration_by_sector, free_movement_stats, intra_regional_trade

router = DefaultRouter()
router.register(r"migrant-flows", ECOWASMigrantFlowViewSet, basename="ecowasmigrant")
router.register(r"trade-flows", ECOWASTradeFlowViewSet, basename="ecowastrade")
router.register(r"config", ECOWASConfigurationViewSet, basename="ecowasconfig")

urlpatterns = [
    path("", include(router.urls)),
    path("corridors/", migration_corridors, name="ecowas-corridors"),
    path("by-sector/", migration_by_sector, name="ecowas-sector"),
    path("free-movement/", free_movement_stats, name="ecowas-free-movement"),
    path("intra-trade/", intra_regional_trade, name="ecowas-intra-trade"),
]