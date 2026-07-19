from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import DataQualityRule, DataQualityIssue
from .serializers import DataQualityRuleSerializer, DataQualityIssueSerializer

class DataQualityRuleViewSet(viewsets.ModelViewSet):
    queryset = DataQualityRule.objects.all()
    serializer_class = DataQualityRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['rule_type', 'model_name', 'is_active', 'severity']

class DataQualityIssueViewSet(viewsets.ModelViewSet):
    serializer_class = DataQualityIssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'model_name', 'severity']

    def get_queryset(self):
        return DataQualityIssue.objects.select_related('rule')

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        issue = self.get_object()
        issue.status = 'resolved'
        issue.resolved_by = request.user
        from django.utils import timezone
        issue.resolved_at = timezone.now()
        issue.save()
        return Response({'status': 'resolved'})

    @action(detail=True, methods=['post'])
    def ignore(self, request, pk=None):
        issue = self.get_object()
        issue.status = 'ignored'
        issue.resolved_by = request.user
        from django.utils import timezone
        issue.resolved_at = timezone.now()
        issue.save()
        return Response({'status': 'ignored'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def quality_overview(request):
    """Data quality dashboard stats."""
    total_issues = DataQualityIssue.objects.count()
    open_issues = DataQualityIssue.objects.filter(status='open').count()
    resolved_issues = DataQualityIssue.objects.filter(status='resolved').count()

    by_model = {}
    for model in DataQualityIssue.objects.values('model_name').distinct():
        model_name = model['model_name']
        by_model[model_name] = DataQualityIssue.objects.filter(model_name=model_name, status='open').count()

    return Response({
        'total_issues': total_issues,
        'open_issues': open_issues,
        'resolved_issues': resolved_issues,
        'ignored_issues': DataQualityIssue.objects.filter(status='ignored').count(),
        'by_model': by_model,
        'open_by_severity': {
            'error': DataQualityIssue.objects.filter(status='open', rule__severity='error').count(),
            'warning': DataQualityIssue.objects.filter(status='open', rule__severity='warning').count(),
        }
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def run_quality_check(request):
    """Trigger manual quality check."""
    from .tasks import run_data_quality_scan
    run_data_quality_scan.delay()
    return Response({'status': 'scan_started'})
