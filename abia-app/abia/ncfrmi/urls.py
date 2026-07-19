from django.urls import path
from .views import sync_single_migrant, bulk_sync_migrants, sync_status, sync_history

urlpatterns = [
    path("sync-migrant/<uuid:migrant_id>/", sync_single_migrant, name="ncfrmi-sync-single"),
    path("bulk-sync/", bulk_sync_migrants, name="ncfrmi-bulk-sync"),
    path("sync-status/<uuid:sync_id>/", sync_status, name="ncfrmi-sync-status"),
    path("sync-history/", sync_history, name="ncfrmi-sync-history"),
]