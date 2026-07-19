from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import (
    get_migration_overview,
    get_cases_by_lga,
    get_cases_by_type,
    get_monthly_trends,
    get_risk_distribution,
    get_recent_activity,
)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    return Response(get_migration_overview())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_cases_by_lga(request):
    return Response(get_cases_by_lga())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_cases_by_type(request):
    return Response(get_cases_by_type())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_monthly_trends(request):
    months = int(request.query_params.get("months", 12))
    return Response(get_monthly_trends(months=months))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_risk_distribution(request):
    return Response(get_risk_distribution())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_recent_activity(request):
    limit = int(request.query_params.get("limit", 20))
    return Response(get_recent_activity(limit=limit))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_dashboard(request):
    return Response({
        "overview": get_migration_overview(),
        "cases_by_lga": get_cases_by_lga(),
        "cases_by_type": get_cases_by_type(),
        "monthly_trends": get_monthly_trends(),
        "risk_distribution": get_risk_distribution(),
        "recent_activity": get_recent_activity(),
    })
