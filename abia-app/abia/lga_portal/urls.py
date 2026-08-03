from django.urls import path
from . import views

app_name = 'lga_portal'

urlpatterns = [
    path("", views.lga_dashboard, name="dashboard"),
    path("victims/", views.lga_victims, name="victims"),
    path("shelters/", views.lga_shelters, name="shelters"),
    path("cases/", views.lga_cases, name="cases"),
    path("events/", views.lga_events, name="events"),
]
