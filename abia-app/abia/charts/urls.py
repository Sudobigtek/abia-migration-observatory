from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChartDashboardViewSet, chart_data, preset_charts, analytics_summary

router = DefaultRouter()
router.register(r"dashboards", ChartDashboardViewSet, basename="chartdashboard")

urlpatterns = [
    path("", include(router.urls)),
    path("data/<uuid:dashboard_id>/", chart_data, name="chart-data"),
    path("presets/", preset_charts, name="chart-presets"),
    path("summary/", analytics_summary, name="chart-summary"),
]