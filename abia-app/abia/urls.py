from django.contrib import admin
from django.urls import include, path
from abia.common.metadata import api_metadata, health_check
from django.views.generic import TemplateView

from abia.dashboard_view import unified_dashboard
from abia.ncfrmi_reporting import urls as ncfrmi_urls
from abia.giz import urls as giz_urls
from abia.sports import urls as sports_urls
from abia.ecowas import urls as ecowas_urls
from abia.wto import urls as wto_urls
from abia.worldbank import urls as wb_urls
from abia.cbn import urls as cbn_urls
from abia.iom import urls as iom_urls
from abia.backup import urls as backup_urls
from abia.maps import urls as maps_urls
from abia.importers import urls as importers_urls
from abia.charts import urls as charts_urls
from abia.webhooks import urls as webhooks_urls
from abia.throttle import urls as throttle_urls
from abia.hotspot import urls as hotspot_urls
from abia.ncfrmi import urls as ncfrmi_api_urls
from abia.tenant import urls as tenant_urls
from abia.notifications import urls as notif_urls
from abia.common.views import api_version_info, cache_stats_view
from abia.common.middleware import health_check, metrics_endpoint
from abia.common.gateway import gateway_status, gateway_routes, gateway_key_rotate

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

# Report views
from abia.ncfrmi_reporting.views import (
    report_list, ncfrmi_report_detail, ncfrmi_generate, ncfrmi_submit
)
from abia.giz.views import (
    giz_migration_governance, giz_reintegration, giz_protection
)
from abia.iom.views import (
    iom_migration_management, iom_avr_report, iom_counter_trafficking_report,
    iom_capacity_building_report, iom_submit_report
)
from abia.governor.views import executive_summary

# Mobile + API views
from abia.mobile.views import (
    mobile_dashboard, mobile_migrant_register, mobile_case_open
)
from abia.api.views import dashboard_stats_api, hotspot_geojson_api


urlpatterns = [    
    path("api/v1/metadata/", api_metadata, name="api-metadata"),
    path("api/v1/health/", health_check, name="api-health"),
    path('', include('abia.public_dashboard.urls')),
    # Dashboard
    path("dashboard/", TemplateView.as_view(template_name="dashboard/index.html"), name="dashboard"),

    # Reports
    path("reports/", report_list, name="report_list"),
    path("reports/ncfrmi/<int:pk>/", ncfrmi_report_detail, name="ncfrmi_report_detail"),
    path("reports/ncfrmi/generate/", ncfrmi_generate, name="ncfrmi_generate"),
    path("reports/ncfrmi/<int:pk>/submit/", ncfrmi_submit, name="ncfrmi_submit"),
    path("reports/giz/migration-governance/", giz_migration_governance, name="giz_migration_governance"),
    path("reports/giz/reintegration/", giz_reintegration, name="giz_reintegration"),
    path("reports/giz/protection/", giz_protection, name="giz_protection"),
    path("reports/iom/migration-management/", iom_migration_management, name="iom_migration_management"),
    path("reports/iom/avr/", iom_avr_report, name="iom_avr_report"),
    path("reports/iom/counter-trafficking/", iom_counter_trafficking_report, name="iom_counter_trafficking"),
    path("reports/iom/capacity-building/", iom_capacity_building_report, name="iom_capacity_building"),
    path("reports/iom/<int:pk>/submit/", iom_submit_report, name="iom_submit_report"),
    path("reports/governor/executive-summary/", executive_summary, name="governor_executive_summary"),

    # Mobile
    path("mobile/", mobile_dashboard, name="mobile_dashboard"),
    path("mobile/migrant/register/", mobile_migrant_register, name="mobile_migrant_register"),
    path("mobile/case/open/", mobile_case_open, name="mobile_case_open"),

    # API
    path("api/dashboard/stats/", dashboard_stats_api, name="dashboard_stats_api"),
    path("api/hotspots/geojson/", hotspot_geojson_api, name="hotspot_geojson_api"),

    # Landing + Admin
    path("", TemplateView.as_view(template_name="landing.html"), name="home"),
    path("admin/", admin.site.urls),

    # Health + Metrics
    path("health/", health_check, name="health-check"),
    path("metrics/", metrics_endpoint, name="prometheus-metrics"),

    # API Version + Gateway
    path("api/version/", api_version_info, name="api-version"),
    path("api/gateway/status/", gateway_status, name="gateway-status"),
    path("api/gateway/routes/", gateway_routes, name="gateway-routes"),
    path("api/gateway/key-rotate/", gateway_key_rotate, name="gateway-key-rotate"),
    path("api/cache-stats/", cache_stats_view, name="cache-stats"),

    # Auth
    path("accounts/", include("allauth.urls")),
    path("api/v1/auth/token/", obtain_auth_token, name="token-auth"),
    path("api-auth/", include("rest_framework.urls")),

    # API Routes
    path("api/v1/", include("abia.accounts.urls")),
    path("api/v1/", include("abia.migrants.urls")),
    path("api/v1/", include("abia.cases.urls")),
    path("api/v1/", include("abia.referrals.urls")),
    path("api/v1/dynamic-fields/", include("dynamic_fields.urls")),
    path("api/v1/notifications/", include(notif_urls)),
    path("api/v1/charts/", include(charts_urls)),
    path("api/v1/importers/", include(importers_urls)),
    path("api/v1/maps/", include(maps_urls)),
    path("api/v1/backup/", include(backup_urls)),
    path("api/v1/iom/", include(iom_urls)),
    path("api/v1/webhooks/", include(webhooks_urls)),
    path("api/v1/push/", include("abia.push.urls")),
    path("api/v1/geo/", include("abia.geo.urls")),
    path("api/v1/reports/", include("abia.reports.urls")),
    path("api/v1/throttle/", include(throttle_urls)),
    path("api/v1/quality/", include("abia.quality.urls")),
    path("api/v1/search/", include("abia.search.urls")),
    path("api/v1/workflows/", include("abia.workflows.urls")),
    path("api/v1/documents/", include("abia.documents.urls")),
    path("api/v1/audit/", include("abia.audit.urls")),
    path("api/v1/tenant/", include(tenant_urls)),
    path("api/v1/ncfrmi/", include(ncfrmi_api_urls)),
    path("api/v1/hotspot/", include(hotspot_urls)),
    path("api/v1/analytics/", include("abia.analytics.urls")),
    path("api/v1/pwa/", include("abia.pwa.urls")),
    path("api/v1/cbn/", include(cbn_urls)),
    path("api/v1/worldbank/", include(wb_urls)),
    path("api/v1/wto/", include(wto_urls)),
    path("api/v1/ecowas/", include(ecowas_urls)),
    path("api/v1/sports/", include(sports_urls)),
    path("api/v1/ncfrmi-reporting/", include(ncfrmi_urls)),
    path("api/v1/giz/", include(giz_urls)),

    # Schema + Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
