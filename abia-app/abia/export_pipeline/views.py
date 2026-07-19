from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse
from .models import DataExport
from .tasks import generate_export

class DataExportViewSet(viewsets.ModelViewSet):
    queryset = DataExport.objects.select_related("created_by")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        from .serializers import DataExportSerializer
        return DataExportSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        export = self.get_object()
        if export.status not in ["pending", "failed"]:
            return Response({"error": "Export already processed"}, status=400)
        export.status = "pending"
        export.error_message = ""
        export.save(update_fields=["status", "error_message"])
        generate_export.delay(str(export.id))
        return Response({
            "status": "queued",
            "export_id": str(export.id),
            "message": "Export generation started"
        })

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        export = self.get_object()
        if export.status != "completed" or not export.file_path:
            return Response({"error": "Export not ready"}, status=400)
        try:
            return FileResponse(
                open(export.file_path, "rb"),
                as_attachment=True,
                filename=f"{export.name}.{export.export_format}"
            )
        except FileNotFoundError:
            return Response({"error": "File not found"}, status=404)

    @action(detail=True, methods=["get"])
    def ipfs(self, request, pk=None):
        export = self.get_object()
        if not export.ipfs_hash:
            return Response({"error": "Not published to IPFS"}, status=400)
        return Response({
            "ipfs_hash": export.ipfs_hash,
            "ipfs_url": export.ipfs_url,
            "gateway_urls": [
                f"https://ipfs.io/ipfs/{export.ipfs_hash}",
                f"https://gateway.pinata.cloud/ipfs/{export.ipfs_hash}",
            ]
        })
