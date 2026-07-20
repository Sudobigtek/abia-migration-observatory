from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import SearchService
from .serializers import SearchIndexSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search(request):
    query = request.query_params.get("q", "")
    entity_type = request.query_params.get("type")
    lga_id = request.query_params.get("lga")
    limit = int(request.query_params.get("limit", 50))
    results = SearchService.search(query, entity_type, lga_id, limit)
    serializer = SearchIndexSerializer(results, many=True)
    return Response({
        "query": query,
        "count": len(serializer.data),
        "results": serializer.data
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rebuild_index(request):
    count = SearchService.rebuild_index()
    return Response({"status": "rebuilt", "indexed_count": count})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_facets(request):
    from .models import SearchIndex
    from django.db.models import Count
    facets = {
        "entity_types": list(SearchIndex.objects.values("entity_type").annotate(count=Count("id")).values("entity_type", "count")),
        "total_indexed": SearchIndex.objects.count(),
    }
    return Response(facets)