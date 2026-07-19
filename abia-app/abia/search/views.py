from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import F, Q
from .models import SearchIndex

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_search(request):
    """Full-text search across all indexed entities."""
    query = request.query_params.get('q', '').strip()
    entity_type = request.query_params.get('type', None)
    limit = min(int(request.query_params.get('limit', 20)), 100)
    
    if not query or len(query) < 2:
        return Response({'error': 'Query must be at least 2 characters'}, status=400)
    
    # Build search query
    search_query = SearchQuery(query, config='english')
    
    # Base queryset
    queryset = SearchIndex.objects.annotate(
        rank=SearchRank(F('search_vector'), search_query),
        similarity=TrigramSimilarity('title', query)
    ).filter(
        Q(search_vector=search_query) | Q(similarity__gt=0.3)
    )
    
    # Filter by entity type if specified
    if entity_type:
        queryset = queryset.filter(entity_type=entity_type)
    
    # Order by rank + similarity
    results = queryset.order_by('-rank', '-similarity')[:limit]
    
    data = [{
        'id': str(r.id),
        'entity_type': r.entity_type,
        'entity_id': str(r.entity_id),
        'title': r.title,
        'content': r.content[:200] + '...' if len(r.content) > 200 else r.content,
        'metadata': r.metadata,
        'score': round(float(r.rank or 0) + float(r.similarity or 0), 4),
        'created_at': r.created_at.isoformat(),
    } for r in results]
    
    return Response({
        'query': query,
        'count': len(data),
        'results': data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_reindex(request):
    """Trigger reindexing of all searchable entities."""
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    from abia.referrals.models import Referral
    
    created = 0
    updated = 0
    
    # Index migrants
    for migrant in Migrant.objects.all():
        content = f"{migrant.full_name} {migrant.phone or ''} {migrant.email or ''} {migrant.nationality or ''}"
        obj, was_created = SearchIndex.objects.update_or_create(
            entity_type='migrant',
            entity_id=migrant.id,
            defaults={
                'title': migrant.full_name,
                'content': content,
                'metadata': {
                    'status': migrant.status,
                    'gender': migrant.gender,
                    'lga': migrant.current_lga.name if migrant.current_lga else None,
                }
            }
        )
        if was_created:
            created += 1
        else:
            updated += 1
    
    # Index cases
    for case in Case.objects.select_related('migrant').all():
        content = f"{case.description or ''} {case.case_type or ''}"
        obj, was_created = SearchIndex.objects.update_or_create(
            entity_type='case',
            entity_id=case.id,
            defaults={
                'title': f"Case: {case.case_type}",
                'content': content,
                'metadata': {
                    'status': case.status,
                    'priority': case.priority,
                    'migrant_name': case.migrant.full_name if case.migrant else None,
                }
            }
        )
        if was_created:
            created += 1
        else:
            updated += 1
    
    # Update search vectors
    for idx in SearchIndex.objects.filter(search_vector__isnull=True):
        idx.update_search_vector()
    
    return Response({
        'status': 'reindexed',
        'created': created,
        'updated': updated,
        'total': SearchIndex.objects.count()
    })
