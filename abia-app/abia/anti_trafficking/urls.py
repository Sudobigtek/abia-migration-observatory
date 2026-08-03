from django.urls import path
from . import views

app_name = 'anti_trafficking'

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]
