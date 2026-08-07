from django.urls import path
from . import views

app_name = 'migration_corps'

urlpatterns = [
    path('', views.corps_dashboard, name='dashboard'),
    path('volunteers/', views.volunteer_list, name='volunteer_list'),
    path('volunteers/<int:pk>/', views.volunteer_detail, name='volunteer_detail'),
    path('verify/', views.verify_volunteer, name='verify_volunteer'),
]
