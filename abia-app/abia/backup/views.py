from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    BackupFilesResponse,
    BackupStatusResponse,
    TriggerBackupResponse,
    TriggerRestoreResponse,
)
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import BackupJob, RestoreJob
from .services import BackupService
from .serializers import BackupJobSerializer, RestoreJobSerializer

class BackupJobViewSet(viewsets.ModelViewSet):
    serializer_class = BackupJobSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = BackupJob.objects.all().select_related("created_by")

class RestoreJobViewSet(viewsets.ModelViewSet):
    serializer_class = RestoreJobSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = RestoreJob.objects.all().select_related("backup", "created_by")

@extend_schema(responses=TriggerBackupResponse, tags=["System"], summary="Trigger manual backup")
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def trigger_backup(request):
    backup_type = request.data.get("backup_type", "full")
    job = BackupJob.objects.create(
        backup_type=backup_type,
        created_by=request.user
    )
    BackupService.run_pg_dump(job)
    serializer = BackupJobSerializer(job)
    return Response(serializer.data)


trigger_backup.cls.serializer_class = TriggerBackupResponse
@extend_schema(responses=TriggerRestoreResponse, tags=["System"], summary="Trigger backup restore")
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def trigger_restore(request):
    backup_id = request.data.get("backup_id")
    if not backup_id:
        return Response({"error": "backup_id required"}, status=400)
    from django.shortcuts import get_object_or_404
    backup = get_object_or_404(BackupJob, id=backup_id)
    restore = RestoreJob.objects.create(backup=backup, created_by=request.user)
    BackupService.run_restore(restore)
    serializer = RestoreJobSerializer(restore)
    return Response(serializer.data)


trigger_restore.cls.serializer_class = TriggerRestoreResponse
@extend_schema(responses=BackupFilesResponse, tags=["System"], summary="List backup files")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def backup_files(request):
    return Response({"backups": BackupService.list_backups()})

@extend_schema(responses=BackupStatusResponse, tags=["System"], summary="Backup system status")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def backup_status(request):
    latest = BackupJob.objects.order_by("-created_at").first()
    if not latest:
        return Response({"last_backup": None, "status": "no_backups"})
    return Response({
        "last_backup": {
            "id": str(latest.id),
            "type": latest.backup_type,
            "status": latest.status,
            "size": latest.file_size,
            "created_at": latest.created_at,
        },
        "status": latest.status
    })


# Propagate _spectacular metadata for drf-spectacular
if hasattr(trigger_backup, '_spectacular') and hasattr(trigger_backup, 'cls'):
    trigger_backup.cls._spectacular = trigger_backup._spectacular
if hasattr(trigger_restore, '_spectacular') and hasattr(trigger_restore, 'cls'):
    trigger_restore.cls._spectacular = trigger_restore._spectacular
if hasattr(backup_files, '_spectacular') and hasattr(backup_files, 'cls'):
    backup_files.cls._spectacular = backup_files._spectacular
if hasattr(backup_status, '_spectacular') and hasattr(backup_status, 'cls'):
    backup_status.cls._spectacular = backup_status._spectacular
