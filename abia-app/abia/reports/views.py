from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ReportTemplate, GeneratedReport
from .serializers import ReportTemplateSerializer, GeneratedReportSerializer

class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.select_related('created_by')
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_type', 'is_active']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class GeneratedReportViewSet(viewsets.ModelViewSet):
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'format']

    def get_queryset(self):
        return GeneratedReport.objects.filter(generated_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user, status='pending')

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Trigger report generation."""
        from .tasks import generate_report_task
        report = self.get_object()
        if report.status == 'pending':
            generate_report_task.delay(str(report.id))
            return Response({'status': 'queued', 'report_id': str(report.id)})
        return Response({'status': report.status, 'message': 'Report already processed'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def report_dashboard(request):
    """Quick report stats for dashboard."""
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    from abia.referrals.models import Referral
    from abia.ai.models import RiskAssessment
    from django.db.models import Count, Avg
    from django.utils import timezone
    import datetime

    today = timezone.now().date()
    month_start = today.replace(day=1)

    return Response({
        'period': {
            'today': str(today),
            'month_start': str(month_start),
        },
        'migrants': {
            'total': Migrant.objects.count(),
            'this_month': Migrant.objects.filter(created_at__date__gte=month_start).count(),
            'by_status': dict(Migrant.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')),
        },
        'cases': {
            'total': Case.objects.count(),
            'open': Case.objects.filter(status='open').count(),
            'resolved_this_month': Case.objects.filter(status='resolved', resolved_at__date__gte=month_start).count(),
        },
        'referrals': {
            'total': Referral.objects.count(),
            'pending': Referral.objects.filter(status='pending').count(),
            'completed_this_month': Referral.objects.filter(status='completed', updated_at__date__gte=month_start).count(),
        },
        'risk': {
            'high_risk_count': RiskAssessment.objects.filter(risk_level__in=['high', 'critical']).count(),
            'avg_score': RiskAssessment.objects.aggregate(avg=Avg('risk_score'))['avg'] or 0,
        }
    })
