"""
ABIA Migration Observatory — Root URL Configuration
Clean, minimal, production-oriented routing.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

# Dashboard views (Batch 1)
from abia.dashboard.views import public_dashboard, command_center, dashboard

urlpatterns = [
    # ---------- Public ----------
    path("", TemplateView.as_view(template_name="landing.html"), name="home"),
    path("public-dashboard/", public_dashboard, name="public_dashboard"),

    # ---------- Authenticated dashboards ----------
    path("dashboard/", dashboard, name="dashboard"),
    path("command-center/", command_center, name="command_center"),

    # ---------- Admin ----------
    path("admin/", admin.site.urls),

    # ---------- Core API modules (safe includes) ----------
    path("api/v1/accounts/", include("abia.accounts.urls")),
    path("api/v1/cases/", include("abia.cases.urls")),
    path("api/v1/anti-trafficking/", include("abia.anti_trafficking.urls")),
    path("api/v1/analytics/", include("abia.analytics.urls")),
    path("api/v1/charts/", include("abia.charts.urls")),
    path("api/v1/ai/", include("abia.ai.urls")),
    path("api/v1/audit/", include("abia.audit.urls")),
    path("api/v1/backup/", include("abia.backup.urls")),
    path("api/v1/cbn/", include("abia.cbn.urls")),
]
