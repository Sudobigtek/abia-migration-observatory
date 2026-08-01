"""URL routing for public dashboard app."""
from django.urls import path
from . import views

app_name = "public_dashboard"

urlpatterns = [
    path("", views.public_dashboard, name="dashboard"),
    path("map-data/", views.public_map_data, name="map_data"),
    path("feedback/", views.public_feedback, name="feedback"),
    path("feedback/success/", views.feedback_success, name="feedback_success"),
    path("sdg/", views.sdg_dashboard, name="sdg_dashboard"),
    path("register/", views.migrant_register, name="migrant_register"),
    path("register/success/", views.registration_success, name="registration_success"),
    path("status/", views.status_check, name="status_check"),
]
