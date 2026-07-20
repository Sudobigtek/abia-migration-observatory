from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import IOMDataExchange, IOMConfiguration
from .services import IOMService
from .serializers import IOMDataExchangeSerializer, IOMConfigurationSerializer

class IOMDataExchangeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IOMDataExchangeSerializer
    permission_classes = [IsAuthenticated]
    queryset = IOMDataExchange.objects.all().select_related("processed_by")

class IOMConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = IOMConfigurationSerializer
    permission_classes = [IsAuthenticated]
    queryset = IOMConfiguration.objects.all()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_migrants_to_iom(request):
    results = IOMService.sync_all_to_iom("migrant")
    return Response(results)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_cases_to_iom(request):
    results = IOMService.sync_all_to_iom("case")
    return Response(results)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def iom_stats(request):
    from django.db.models import Count
    stats = {
        "total_exchanges": IOMDataExchange.objects.count(),
        "completed": IOMDataExchange.objects.filter(status="completed").count(),
        "failed": IOMDataExchange.objects.filter(status="failed").count(),
        "pending": IOMDataExchange.objects.filter(status="pending").count(),
        "by_entity": list(IOMDataExchange.objects.values("entity_type").annotate(count=Count("id")).values("entity_type", "count")),
        "by_direction": list(IOMDataExchange.objects.values("direction").annotate(count=Count("id")).values("direction", "count")),
    }
    return Response(stats)