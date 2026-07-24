"""URL configuration for public dashboard."""
from django.urls import path
from . import views

app_name = "public_dashboard"

urlpatterns = [
    path("", views.public_dashboard, name="public_dashboard"),
    path("dashboard/", views.public_dashboard, name="public_dashboard_stats"),
    path("map-data/", views.public_map_data, name="public_map_data"),
    path("feedback/", views.public_feedback, name="public_feedback"),
    path("feedback/success/", views.feedback_success, name="feedback_success"),
    path("sdg-gcm/", views.sdg_dashboard, name="sdg_dashboard"),
    path("register/", views.migrant_register, name="migrant_register"),
    path("register/success/", views.registration_success, name="registration_success"),
    path("status/", views.status_check, name="status_check"),
]