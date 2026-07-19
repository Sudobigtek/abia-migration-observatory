from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog, ComplianceReport
from .services import generate_compliance_report
from .serializers import AuditLogSerializer, ComplianceReportSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("user")
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["action", "entity_type", "user", "created_at"]
    serializer_class = AuditLogSerializer

class ComplianceReportViewSet(viewsets.ModelViewSet):
    queryset = ComplianceReport.objects.select_related("generated_by")
    permission_classes = [IsAuthenticated]
    serializer_class = ComplianceReportSerializer

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_report(request):
    period_start = request.data.get("period_start")
    period_end = request.data.get("period_end")
    report_type = request.data.get("report_type", "ad_hoc")
    if not period_start or not period_end:
        return Response({"error": "period_start and period_end required"}, status=400)
    data = generate_compliance_report(period_start, period_end, report_type)
    report = ComplianceReport.objects.create(
        title=report_type.title() + " Report " + str(period_start) + " to " + str(period_end),
        report_type=report_type,
        period_start=period_start,
        period_end=period_end,
        data=data,
        generated_by=request.user
    )
    return Response({"status": "generated", "report_id": str(report.id), "data": data})