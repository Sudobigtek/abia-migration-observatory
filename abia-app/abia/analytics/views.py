from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    AnalyticsCasesByLgaResponse,
    AnalyticsCasesByTypeResponse,
    AnalyticsDashboardResponse,
    AnalyticsMonthlyTrendsResponse,
    AnalyticsOverviewResponse,
    AnalyticsRecentActivityResponse,
    AnalyticsRiskDistributionResponse,
)
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

@extend_schema(responses=AnalyticsOverviewResponse, tags=["Analytics"], summary="High-level analytics overview")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    return Response(get_migration_overview())

@extend_schema(responses=AnalyticsCasesByLgaResponse, tags=["Analytics"], summary="Cases grouped by LGA")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_cases_by_lga(request):
    return Response(get_cases_by_lga())

@extend_schema(responses=AnalyticsCasesByTypeResponse, tags=["Analytics"], summary="Cases grouped by type")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_cases_by_type(request):
    return Response(get_cases_by_type())

@extend_schema(responses=AnalyticsMonthlyTrendsResponse, tags=["Analytics"], summary="Monthly case/migrant trends")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_monthly_trends(request):
    months = int(request.query_params.get("months", 12))
    return Response(get_monthly_trends(months=months))

@extend_schema(responses=AnalyticsRiskDistributionResponse, tags=["Analytics"], summary="Risk level distribution")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_risk_distribution(request):
    return Response(get_risk_distribution())

@extend_schema(responses=AnalyticsRecentActivityResponse, tags=["Analytics"], summary="Recent system activity feed")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_recent_activity(request):
    limit = int(request.query_params.get("limit", 20))
    return Response(get_recent_activity(limit=limit))

@extend_schema(responses=AnalyticsDashboardResponse, tags=["Analytics"], summary="Dashboard overview metrics")
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


# Propagate _spectacular metadata for drf-spectacular
if hasattr(analytics_overview, '_spectacular') and hasattr(analytics_overview, 'cls'):
    analytics_overview.cls._spectacular = analytics_overview._spectacular
if hasattr(analytics_cases_by_lga, '_spectacular') and hasattr(analytics_cases_by_lga, 'cls'):
    analytics_cases_by_lga.cls._spectacular = analytics_cases_by_lga._spectacular
if hasattr(analytics_cases_by_type, '_spectacular') and hasattr(analytics_cases_by_type, 'cls'):
    analytics_cases_by_type.cls._spectacular = analytics_cases_by_type._spectacular
if hasattr(analytics_monthly_trends, '_spectacular') and hasattr(analytics_monthly_trends, 'cls'):
    analytics_monthly_trends.cls._spectacular = analytics_monthly_trends._spectacular
if hasattr(analytics_risk_distribution, '_spectacular') and hasattr(analytics_risk_distribution, 'cls'):
    analytics_risk_distribution.cls._spectacular = analytics_risk_distribution._spectacular
if hasattr(analytics_recent_activity, '_spectacular') and hasattr(analytics_recent_activity, 'cls'):
    analytics_recent_activity.cls._spectacular = analytics_recent_activity._spectacular
if hasattr(analytics_dashboard, '_spectacular') and hasattr(analytics_dashboard, 'cls'):
    analytics_dashboard.cls._spectacular = analytics_dashboard._spectacular
