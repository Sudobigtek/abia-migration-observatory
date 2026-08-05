
from django.urls import path
from . import views

app_name = "japa_development"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("beneficiaries/", views.beneficiary_list, name="beneficiary_list"),
    path("beneficiaries/<int:pk>/", views.beneficiary_detail, name="beneficiary_detail"),
    path("api/dashboard-data/", views.api_dashboard_data, name="api_dashboard_data"),
]
