from abia import views
from django.contrib import admin
from django.urls import include, path
from abia.hotspot import urls as hotspot_urls
from abia.ncfrmi import urls as ncfrmi_urls
from abia.tenant import urls as tenant_urls
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

from abia.common.middleware import health_check, metrics_endpoint
from django.views.generic import TemplateView
from abia.notifications import urls as notif_urls
from abia.common.views import api_version_info, cache_stats_view
from abia.webhooks import urls as webhook_urls
from abia.push import urls as push_urls
from abia.geo import urls as geo_urls
from abia.reports import urls as reports_urls
from abia.quality import urls as quality_urls
from abia.workflows import urls as workflow_urls
from abia.documents import urls as documents_urls
from abia.audit import urls as audit_urls
from abia.pwa import urls as pwa_urls
from abia.analytics import urls as analytics_urls
from abia.search import urls as search_urls
from abia.common.gateway import gateway_status, gateway_routes, gateway_key_rotate

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),
    path("api/version/", api_version_info, name="api-version"),
    path("api/gateway/key-rotate/", gateway_key_rotate, name="gateway-key-rotate"),
    path("api/gateway/routes/", gateway_routes, name="gateway-routes"),
    path("api/gateway/status/", gateway_status, name="gateway-status"),
    path("api/cache-stats/", cache_stats_view, name="cache-stats"),
    path("api/v1/dynamic-fields/", include("dynamic_fields.urls")),
    path("api/v1/notifications/", include(notif_urls)),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("health/", health_check, name="health-check"),
    path("metrics/", metrics_endpoint, name="prometheus-metrics"),
    path("api/v1/auth/token/", obtain_auth_token, name="token-auth"),
    path("api/v1/", include("abia.accounts.urls")),
    path("api/v1/", include("abia.migrants.urls")),
    path("api/v1/", include("abia.cases.urls")),
    path("api/v1/", include("abia.referrals.urls")),
    path("api/v1/webhooks/", include(webhook_urls)),
    path("api/v1/push/", include(push_urls)),
    path("api/v1/geo/", include(geo_urls)),
    path("api/v1/reports/", include(reports_urls)),
    path("api/v1/quality/", include(quality_urls)),
    path("api/v1/search/", include(search_urls)),
    path("api/v1/workflows/", include(workflow_urls)),
    path("api/v1/documents/", include(documents_urls)),
    path("api/v1/audit/", include(audit_urls)),
    path("api/v1/tenant/", include(tenant_urls)),
    path("api/v1/ncfrmi/", include(ncfrmi_urls)),
    path("api/v1/hotspot/", include(hotspot_urls)),
    path("api/v1/analytics/", include(analytics_urls)),
    path("pwa/", include(pwa_urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api-auth/", include("rest_framework.urls")),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("migrants/", views.migrant_list_view, name="migrant-list"),
    path("cases/detail/", views.case_detail_view, name="case-detail"),
    path("referrals/new/", views.referral_form_view, name="referral-form"),
]