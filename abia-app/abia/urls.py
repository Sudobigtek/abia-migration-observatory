from django.contrib import admin
from django.urls import path, include
from abia.dashboard_view import landing, onboarding

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),
    path('onboarding/', onboarding, name='onboarding'),
    path('command-center/', include('abia.charts.urls')),
    path('reports/', include('abia.reports.urls')),
    path('public-dashboard/', include('abia.public_dashboard.urls')),
]
