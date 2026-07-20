from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ReportTemplate, GeneratedReport
from .services import ReportService
from .serializers import ReportTemplateSerializer, GeneratedReportSerializer

class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class GeneratedReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedReport.objects.select_related("template", "generated_by")
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated]

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_report(request):
    template_id = request.data.get("template_id")
    params = request.data.get("parameters", {})
    if not template_id:
        return Response({"error": "template_id required"}, status=400)
    try:
        template = ReportTemplate.objects.get(id=template_id)
    except ReportTemplate.DoesNotExist:
        return Response({"error": "Template not found"}, status=404)
    report = ReportService.build_report(template, params, request.user)
    serializer = GeneratedReportSerializer(report)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def report_types(request):
    return Response({
        "types": [
            {"id": "migrants", "name": "Migrant Report"},
            {"id": "cases", "name": "Case Report"},
            {"id": "referrals", "name": "Referral Report"},
            {"id": "analytics", "name": "Analytics Report"},
            {"id": "custom", "name": "Custom Report"},
        ]
    })