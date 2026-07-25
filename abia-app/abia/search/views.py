from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    RebuildIndexResponse,
    SearchFacetsResponse,
    SearchResponse,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import SearchService
from .serializers import SearchIndexSerializer

@extend_schema(responses=SearchResponse, tags=["Search"], summary="Search across all entities")
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

@extend_schema(responses=RebuildIndexResponse, tags=["Search"], summary="Rebuild search index")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rebuild_index(request):
    count = SearchService.rebuild_index()
    return Response({"status": "rebuilt", "indexed_count": count})


rebuild_index.cls.serializer_class = RebuildIndexResponse
@extend_schema(responses=SearchFacetsResponse, tags=["Search"], summary="Search facets")
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


# Propagate _spectacular metadata for drf-spectacular
if hasattr(search, '_spectacular') and hasattr(search, 'cls'):
    search.cls._spectacular = search._spectacular
if hasattr(rebuild_index, '_spectacular') and hasattr(rebuild_index, 'cls'):
    rebuild_index.cls._spectacular = rebuild_index._spectacular
if hasattr(search_facets, '_spectacular') and hasattr(search_facets, 'cls'):
    search_facets.cls._spectacular = search_facets._spectacular
