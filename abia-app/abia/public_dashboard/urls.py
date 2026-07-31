from django.urls import path
from abia.public_dashboard import views

app_name = 'public_dashboard'
urlpatterns = [
    path('', views.public_dashboard, name='dashboard'),
]
