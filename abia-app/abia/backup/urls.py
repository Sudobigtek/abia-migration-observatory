from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BackupJobViewSet, RestoreJobViewSet, trigger_backup, trigger_restore, backup_files, backup_status

router = DefaultRouter()
router.register(r"jobs", BackupJobViewSet, basename="backupjob")
router.register(r"restores", RestoreJobViewSet, basename="restorejob")

urlpatterns = [
    path("", include(router.urls)),
    path("trigger/", trigger_backup, name="backup-trigger"),
    path("restore/", trigger_restore, name="backup-restore"),
    path("files/", backup_files, name="backup-files"),
    path("status/", backup_status, name="backup-status"),
]