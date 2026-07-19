from django.urls import path
from .views import (
    analytics_overview,
    analytics_cases_by_lga,
    analytics_cases_by_type,
    analytics_monthly_trends,
    analytics_risk_distribution,
    analytics_recent_activity,
    analytics_dashboard,
)

urlpatterns = [
    path("overview/", analytics_overview, name="analytics-overview"),
    path("cases-by-lga/", analytics_cases_by_lga, name="analytics-cases-by-lga"),
    path("cases-by-type/", analytics_cases_by_type, name="analytics-cases-by-type"),
    path("monthly-trends/", analytics_monthly_trends, name="analytics-monthly-trends"),
    path("risk-distribution/", analytics_risk_distribution, name="analytics-risk-distribution"),
    path("recent-activity/", analytics_recent_activity, name="analytics-recent-activity"),
    path("dashboard/", analytics_dashboard, name="analytics-dashboard"),
]
