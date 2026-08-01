from django.urls import path
from . import views

urlpatterns = [
    path('migrants/', views.migrant_list, name='api_migrants'),
    path('cases/', views.case_list, name='api_cases'),
    path('referrals/', views.referral_list, name='api_referrals'),
]
