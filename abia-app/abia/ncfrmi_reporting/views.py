from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import NCFRMIMonthlyReport, NCFRMISubmissionLog
from .services import NCFRMIReportingService
from .serializers import NCFRMIMonthlyReportSerializer, NCFRMISubmissionLogSerializer

class NCFRMIMonthlyReportViewSet(viewsets.ModelViewSet):
    serializer_class = NCFRMIMonthlyReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return NCFRMIMonthlyReport.objects.all()
        return NCFRMIMonthlyReport.objects.filter(prepared_by=user)

    def perform_create(self, serializer):
        serializer.save(prepared_by=self.request.user)

class NCFRMISubmissionLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NCFRMISubmissionLogSerializer
    permission_classes = [IsAuthenticated]
    queryset = NCFRMISubmissionLog.objects.all()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_monthly(request):
    month = request.data.get("month")
    year = request.data.get("year")
    if not month or not year:
        return Response({"error": "month and year required"}, status=400)
    report = NCFRMIReportingService.generate_monthly_report(int(month), int(year), request.user)
    serializer = NCFRMIMonthlyReportSerializer(report)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_report(request, report_id):
    report = NCFRMIReportingService.submit_to_ncfrmi(report_id, request.user)
    serializer = NCFRMIMonthlyReportSerializer(report)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_report(request, report_id):
    report = NCFRMIReportingService.approve_report(report_id, request.user)
    serializer = NCFRMIMonthlyReportSerializer(report)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def report_stats(request):
    from django.db.models import Count
    return Response({
        "total_reports": NCFRMIMonthlyReport.objects.count(),
        "draft": NCFRMIMonthlyReport.objects.filter(status="draft").count(),
        "pending_approval": NCFRMIMonthlyReport.objects.filter(status="pending_approval").count(),
        "approved": NCFRMIMonthlyReport.objects.filter(status="approved").count(),
        "submitted": NCFRMIMonthlyReport.objects.filter(status="submitted").count(),
        "acknowledged": NCFRMIMonthlyReport.objects.filter(status="acknowledged").count(),
    })