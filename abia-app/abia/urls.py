from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from abia.public_dashboard.views import DashboardView
from abia.dashboard_view import landing, onboarding

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),
    path('onboarding/', onboarding, name='onboarding'),
    path('dashboard/', login_required(DashboardView.as_view()), name='dashboard'),
    path('command-center/', include('abia.charts.urls')),
    path('reports/', include('abia.reports.urls')),
    path('public-dashboard/', include('abia.public_dashboard.urls')),
    path('api/v1/', include('abia.api.urls')),
]
