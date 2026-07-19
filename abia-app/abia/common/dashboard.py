from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_widgets(request):
    """Return all dashboard widget data in one call."""
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    from abia.referrals.models import Referral
    from abia.ai.models import RiskAssessment

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    return Response({
        'kpi_cards': {
            'total_migrants': Migrant.objects.count(),
            'active_cases': Case.objects.filter(status='open').count(),
            'pending_referrals': Referral.objects.filter(status='pending').count(),
            'high_risk_alerts': RiskAssessment.objects.filter(risk_level='critical').count(),
            'new_this_week': Migrant.objects.filter(created_at__date__gte=week_ago).count(),
            'cases_resolved_this_month': Case.objects.filter(status='resolved', resolved_at__date__gte=month_ago).count(),
        },
        'charts': {
            'migrants_by_status': dict(Migrant.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')),
            'cases_by_priority': dict(Case.objects.values('priority').annotate(c=Count('id')).values_list('priority', 'c')),
            'referrals_by_status': dict(Referral.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')),
            'risk_distribution': dict(RiskAssessment.objects.values('risk_level').annotate(c=Count('id')).values_list('risk_level', 'c')),
        },
        'recent_activity': {
            'latest_migrants': list(Migrant.objects.order_by('-created_at').values('full_name', 'status', 'created_at')[:5]),
            'latest_cases': list(Case.objects.order_by('-created_at').values('case_type', 'status', 'priority', 'created_at')[:5]),
            'latest_referrals': list(Referral.objects.order_by('-created_at').values('status', 'created_at')[:5]),
        },
        'alerts': {
            'critical_cases': Case.objects.filter(priority='critical', status='open').count(),
            'overdue_referrals': Referral.objects.filter(status='pending', created_at__date__lt=today - timedelta(days=7)).count(),
            'unresolved_high_risk': RiskAssessment.objects.filter(risk_level='high').exclude(
                migrant__cases__status='resolved'
            ).count(),
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_lga_comparison(request):
    """LGA comparison data for dashboard charts."""
    from abia.accounts.models import LGA
    from abia.migrants.models import Migrant
    from abia.cases.models import Case

    lga_data = []
    for lga in LGA.objects.all()[:10]:
        lga_data.append({
            'lga': lga.name,
            'migrants': Migrant.objects.filter(current_lga=lga).count(),
            'cases': Case.objects.filter(migrant__current_lga=lga, status='open').count(),
            'avg_risk': RiskAssessment.objects.filter(migrant__current_lga=lga).aggregate(avg=Avg('risk_score'))['avg'] or 0,
        })

    return Response({
        'lga_comparison': lga_data,
        'top_lga_by_migrants': sorted(lga_data, key=lambda x: x['migrants'], reverse=True)[:5]
    })
