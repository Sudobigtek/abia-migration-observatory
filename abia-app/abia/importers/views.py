from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ImportJob
from .services import ImportService
from .serializers import ImportJobSerializer

class ImportJobViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ImportJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ImportJob.objects.filter(created_by=self.request.user).select_related("created_by")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    entity_type = request.data.get("entity_type")
    file_obj = request.FILES.get("file")
    if not entity_type or not file_obj:
        return Response({"error": "entity_type and file required"}, status=400)
    if not file_obj.name.endswith(".csv"):
        return Response({"error": "Only CSV files allowed"}, status=400)
    job = ImportJob.objects.create(
        entity_type=entity_type,
        file_name=file_obj.name,
        file_path="",
        created_by=request.user
    )
    result = ImportService.process_import(job, file_obj)
    return Response({"job_id": str(job.id), "status": job.status, "result": result})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def import_template(request, entity_type):
    import csv, io
    output = io.StringIO()
    if entity_type == "migrants":
        writer = csv.DictWriter(output, fieldnames=["full_name", "phone", "email", "gender", "current_lga", "status"])
    elif entity_type == "cases":
        writer = csv.DictWriter(output, fieldnames=["case_type", "description", "status", "priority", "current_lga"])
    else:
        return Response({"error": "Unknown entity type"}, status=400)
    writer.writeheader()
    return Response({"template": output.getvalue(), "entity_type": entity_type})