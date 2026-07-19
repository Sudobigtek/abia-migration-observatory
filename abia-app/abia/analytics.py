from django.db.models import Count, Q, Avg
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.referrals.models import Referral
from abia.ai.models import RiskAssessment

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    """High-level analytics dashboard data."""
    period = request.query_params.get('period', 'month')
    trunc_map = {'day': TruncDay, 'week': TruncWeek, 'month': TruncMonth}
    trunc = trunc_map.get(period, TruncMonth)

    migrant_trends = list(
        Migrant.objects.annotate(period=trunc('created_at'))
        .values('period').annotate(count=Count('id')).order_by('period')
    )
    case_trends = list(
        Case.objects.filter(status='resolved')
        .annotate(period=trunc('closed_at'))
        .values('period').annotate(count=Count('id')).order_by('period')
    )
    total_referrals = Referral.objects.count()
    completed_referrals = Referral.objects.filter(status='completed').count()
    completion_rate = (completed_referrals / total_referrals * 100) if total_referrals > 0 else 0

    return Response({
        'migrant_trends': migrant_trends,
        'case_trends': case_trends,
        'referral_completion_rate': round(completion_rate, 2),
        'risk_distribution': list(RiskAssessment.objects.values('risk_level').annotate(count=Count('id')).order_by('-count')),
        'demographics': {
            'gender': list(Migrant.objects.values('gender').annotate(count=Count('id'))),
            'status': list(Migrant.objects.values('status').annotate(count=Count('id'))),
        },
        'summary': {
            'total_migrants': Migrant.objects.count(),
            'active_cases': Case.objects.filter(status='open').count(),
            'pending_referrals': Referral.objects.filter(status='pending').count(),
            'avg_risk_score': RiskAssessment.objects.aggregate(avg=Avg('risk_score'))['avg'] or 0,
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_lga_breakdown(request):
    """LGA-level breakdown for map visualization."""
    from abia.accounts.models import LGA
    lga_data = []
    for lga in LGA.objects.all():
        lga_data.append({
            'lga_id': str(lga.id),
            'name': lga.name,
            'code': lga.code,
            'migrant_count': Migrant.objects.filter(current_lga=lga).count(),
            'active_cases': Case.objects.filter(migrant__current_lga=lga, status='open').count(),
            'pending_referrals': Referral.objects.filter(migrant__current_lga=lga, status='pending').count(),
            'high_risk_count': RiskAssessment.objects.filter(
                migrant__current_lga=lga, risk_level__in=['high', 'critical']
            ).count(),
        })
    return Response({'lga_breakdown': lga_data, 'total_lgas': len(lga_data)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_export_report(request):
    """Generate and export analytics report as JSON."""
    import json
    from django.http import JsonResponse
    from django.utils import timezone

    report = {
        'generated_at': str(timezone.now()),
        'migrants': {
            'total': Migrant.objects.count(),
            'by_status': dict(Migrant.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')),
            'by_gender': dict(Migrant.objects.values('gender').annotate(c=Count('id')).values_list('gender', 'c')),
        },
        'cases': {
            'total': Case.objects.count(),
            'open': Case.objects.filter(status='open').count(),
            'resolved': Case.objects.filter(status='resolved').count(),
            'by_type': dict(Case.objects.values('case_type').annotate(c=Count('id')).values_list('case_type', 'c')),
        },
        'referrals': {
            'total': Referral.objects.count(),
            'pending': Referral.objects.filter(status='pending').count(),
            'completed': Referral.objects.filter(status='completed').count(),
        },
        'risk': {
            'assessments': RiskAssessment.objects.count(),
            'by_level': dict(RiskAssessment.objects.values('risk_level').annotate(c=Count('id')).values_list('risk_level', 'c')),
            'avg_score': RiskAssessment.objects.aggregate(avg=Avg('risk_score'))['avg'] or 0,
        }
    }
    return JsonResponse(report, json_dumps_params={'indent': 2})
