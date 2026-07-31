from django.urls import path
from abia.reports import views

app_name = 'reports'
urlpatterns = [
    path('', views.partner_dashboard, name='partner_dashboard'),
]
