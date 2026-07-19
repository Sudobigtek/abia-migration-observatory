from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_dashboard(request):
    """Lightweight dashboard for mobile app."""
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    from abia.referrals.models import Referral
    from abia.ai.models import RiskAssessment

    return Response({
        'counts': {
            'migrants': Migrant.objects.count(),
            'active_cases': Case.objects.filter(status='open').count(),
            'pending_referrals': Referral.objects.filter(status='pending').count(),
            'high_risk': RiskAssessment.objects.filter(risk_level__in=['high', 'critical']).count(),
        },
        'recent': {
            'migrants_today': Migrant.objects.filter(created_at__date__gte=__import__('django.utils.timezone').utils.timezone.now().date()).count(),
            'cases_today': Case.objects.filter(created_at__date__gte=__import__('django.utils.timezone').utils.timezone.now().date()).count(),
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_migrant_list(request):
    """Paginated, lightweight migrant list for mobile."""
    from abia.migrants.models import Migrant
    from rest_framework.pagination import PageNumberPagination
    
    paginator = PageNumberPagination()
    paginator.page_size = 20
    
    queryset = Migrant.objects.select_related('current_lga').only(
        'id', 'full_name', 'gender', 'phone', 'status', 'current_lga__name', 'created_at'
    ).order_by('-created_at')
    
    page = paginator.paginate_queryset(queryset, request)
    data = [{
        'id': str(m.id),
        'full_name': m.full_name,
        'gender': m.gender,
        'phone': m.phone,
        'status': m.status,
        'current_lga': m.current_lga.name if m.current_lga else None,
        'created_at': m.created_at.isoformat(),
    } for m in page]
    
    return paginator.get_paginated_response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mobile_quick_case(request):
    """Quick case creation from mobile."""
    from abia.cases.models import Case
    from abia.migrants.models import Migrant
    
    migrant_id = request.data.get('migrant_id')
    case_type = request.data.get('case_type', 'general')
    description = request.data.get('description', '')
    
    if not migrant_id:
        return Response({'error': 'migrant_id required'}, status=400)
    
    try:
        migrant = Migrant.objects.get(id=migrant_id)
        case = Case.objects.create(
            migrant=migrant,
            case_type=case_type,
            description=description,
            status='open',
            priority='medium',
            assigned_to=request.user
        )
        return Response({
            'status': 'created',
            'case_id': str(case.id),
            'case_type': case_type
        })
    except Migrant.DoesNotExist:
        return Response({'error': 'Migrant not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mobile_sync(request):
    """Receive offline sync data from mobile."""
    data = request.data.get('records', [])
    results = {'created': 0, 'updated': 0, 'errors': []}
    
    for record in data:
        # Placeholder: Process each synced record
        pass
    
    return Response({
        'synced': len(data),
        'results': results
    })
