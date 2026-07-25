from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    BulkSyncResponse,
    SyncHistoryResponse,
    SyncSingleResponse,
    SyncStatusResponse,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from abia.migrants.models import Migrant
from .services import NCFRMIService
from .models import NCFRMISyncLog
from .serializers import NCFRMISyncLogSerializer

@extend_schema(responses=SyncSingleResponse, tags=["NCFRMI"], summary="Sync single migrant")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_single_migrant(request, migrant_id):
    migrant = get_object_or_404(Migrant, id=migrant_id)
    log = NCFRMIService.sync_migrant(migrant, request.user)
    return Response({
        "status": log.status,
        "sync_id": str(log.id),
        "ncfrmi_record_id": log.ncfrmi_record_id,
        "error": log.error_message if log.status == "failed" else None
    })


sync_single_migrant.cls.serializer_class = SyncSingleResponse
@extend_schema(responses=BulkSyncResponse, tags=["NCFRMI"], summary="Bulk sync migrants")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def bulk_sync_migrants(request):
    migrant_ids = request.data.get("migrant_ids", [])
    if not migrant_ids:
        return Response({"error": "migrant_ids required"}, status=400)
    migrants = Migrant.objects.filter(id__in=migrant_ids)
    results = NCFRMIService.bulk_sync(migrants, request.user)
    return Response(results)


bulk_sync_migrants.cls.serializer_class = BulkSyncResponse
@extend_schema(responses=SyncStatusResponse, tags=["NCFRMI"], summary="Sync status")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sync_status(request, sync_id):
    log = get_object_or_404(NCFRMISyncLog, id=sync_id)
    serializer = NCFRMISyncLogSerializer(log)
    return Response(serializer.data)

@extend_schema(responses=SyncHistoryResponse, tags=["NCFRMI"], summary="Sync history")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sync_history(request):
    logs = NCFRMISyncLog.objects.select_related("migrant", "synced_by").order_by("-created_at")[:50]
    serializer = NCFRMISyncLogSerializer(logs, many=True)
    return Response(serializer.data)


# Propagate _spectacular metadata for drf-spectacular
if hasattr(sync_single_migrant, '_spectacular') and hasattr(sync_single_migrant, 'cls'):
    sync_single_migrant.cls._spectacular = sync_single_migrant._spectacular
if hasattr(bulk_sync_migrants, '_spectacular') and hasattr(bulk_sync_migrants, 'cls'):
    bulk_sync_migrants.cls._spectacular = bulk_sync_migrants._spectacular
if hasattr(sync_status, '_spectacular') and hasattr(sync_status, 'cls'):
    sync_status.cls._spectacular = sync_status._spectacular
if hasattr(sync_history, '_spectacular') and hasattr(sync_history, 'cls'):
    sync_history.cls._spectacular = sync_history._spectacular
