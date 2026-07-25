from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    QualityDashboardResponse,
    RunChecksResponse,
)
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import DataQualityRule, DataQualityIssue
from .services import QualityService
from .serializers import DataQualityRuleSerializer, DataQualityIssueSerializer

class DataQualityRuleViewSet(viewsets.ModelViewSet):
    queryset = DataQualityRule.objects.all()
    serializer_class = DataQualityRuleSerializer
    permission_classes = [IsAuthenticated]

class DataQualityIssueViewSet(viewsets.ModelViewSet):
    queryset = DataQualityIssue.objects.all()
    serializer_class = DataQualityIssueSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(responses=RunChecksResponse, tags=["Quality"], summary="Run quality checks")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def run_checks(request):
    entity_type = request.data.get("entity_type")
    if entity_type:
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        model_map = {
            "migrants.Migrant": Migrant,
            "cases.Case": Case,
        }
        model_class = model_map.get(entity_type)
        if not model_class:
            return Response({"error": "Unknown entity type"}, status=400)
        total = 0
        for obj in model_class.objects.all():
            total += len(QualityService.run_rules(entity_type, obj))
        return Response({"status": "completed", "issues_found": total})
    total = QualityService.run_all_checks()
    return Response({"status": "completed", "total_issues_found": total})


run_checks.cls.serializer_class = RunChecksResponse
@extend_schema(responses=QualityDashboardResponse, tags=["Quality"], summary="Quality dashboard")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quality_dashboard(request):
    from .models import DataQualityIssue
    from django.db.models import Count
    stats = {
        "total_rules": DataQualityRule.objects.filter(is_active=True).count(),
        "total_issues": DataQualityIssue.objects.count(),
        "open_issues": DataQualityIssue.objects.filter(status="open").count(),
        "by_severity": list(DataQualityIssue.objects.values("severity").annotate(count=Count("id")).values("severity", "count")),
        "by_status": list(DataQualityIssue.objects.values("status").annotate(count=Count("id")).values("status", "count")),
        "migrant_score": QualityService.get_quality_score("migrants.Migrant"),
        "case_score": QualityService.get_quality_score("cases.Case"),
    }
    return Response(stats)


# Propagate _spectacular metadata for drf-spectacular
if hasattr(run_checks, '_spectacular') and hasattr(run_checks, 'cls'):
    run_checks.cls._spectacular = run_checks._spectacular
if hasattr(quality_dashboard, '_spectacular') and hasattr(quality_dashboard, 'cls'):
    quality_dashboard.cls._spectacular = quality_dashboard._spectacular
