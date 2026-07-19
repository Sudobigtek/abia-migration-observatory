from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Migrant


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_migrants(request):
    query = request.query_params.get('q', '').strip()
    if not query or len(query) < 2:
        return Response({'error': 'Query must be at least 2 characters'}, status=400)
    
    vector = SearchVector('full_name', weight='A') +              SearchVector('phone', weight='B') +              SearchVector('email', weight='B') +              SearchVector('state_of_origin', weight='C') +              SearchVector('lga_of_origin', weight='C')
    
    search_query = SearchQuery(query)
    
    results = Migrant.objects.annotate(
        rank=SearchRank(vector, search_query),
        similarity=TrigramSimilarity('full_name', query)
    ).filter(
        Q(rank__gte=0.1) | Q(similarity__gt=0.3)
    ).order_by('-rank', '-similarity')[:20]
    
    data = [{
        'id': str(m.id),
        'full_name': m.full_name,
        'phone': m.phone,
        'email': m.email,
        'status': m.status,
        'current_lga': m.current_lga.name if m.current_lga else None,
        'rank': round(m.rank, 3) if m.rank else 0,
        'similarity': round(m.similarity, 3) if m.similarity else 0,
    } for m in results]
    
    return Response({
        'query': query,
        'count': len(data),
        'results': data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_migrants_simple(request):
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'error': 'Query required'}, status=400)
    
    results = Migrant.objects.filter(
        Q(full_name__icontains=query) |
        Q(phone__icontains=query) |
        Q(email__icontains=query)
    )[:20]
    
    return Response({
        'query': query,
        'count': results.count(),
        'results': [{
            'id': str(m.id),
            'full_name': m.full_name,
            'phone': m.phone,
            'status': m.status
        } for m in results]
    })
