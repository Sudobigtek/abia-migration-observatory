from django.urls import path
from . import views

app_name = 'talent_exchange'

urlpatterns = [
    path('', views.atevs_dashboard, name='dashboard'),
    path('transparency/', views.transparency_public, name='transparency'),
    path('verify-endorsement/', views.verify_endorsement, name='verify_endorsement'),
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('employers/', views.employer_list, name='employer_list'),
]
