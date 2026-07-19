from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Case


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_cases(request):
    query = request.query_params.get('q', '').strip()
    if not query or len(query) < 2:
        return Response({'error': 'Query must be at least 2 characters'}, status=400)
    
    vector = SearchVector('title', weight='A') +              SearchVector('description', weight='B') +              SearchVector('migrant__full_name', weight='A')
    
    search_query = SearchQuery(query)
    
    results = Case.objects.annotate(
        rank=SearchRank(vector, search_query)
    ).filter(rank__gte=0.1).order_by('-rank')[:20]
    
    return Response({
        'query': query,
        'count': len(results),
        'results': [{
            'id': str(c.id),
            'title': c.title,
            'status': c.status,
            'priority': c.priority,
            'migrant_name': c.migrant.full_name if c.migrant else None,
            'rank': round(c.rank, 3) if c.rank else 0,
        } for c in results]
    })
