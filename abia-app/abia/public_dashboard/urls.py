from django.urls import path
from . import views
from django.views.decorators.http import require_http_methods

app_name = "public_dashboard"

urlpatterns = [
    # Portal landing
    path('', views.portal, name='public_landing'),
    path('stats/', views.public_dashboard, name='public_stats'),
    
    # Feedback (multiple aliases for template compatibility)
    path('feedback/', views.public_feedback, name='feedback'),
    path('feedback/success/', views.feedback_success, name='feedback_success'),
    
    # Registration (multiple aliases for template compatibility)
    path('register/', views.migrant_register, name='register'),
    path('register/', views.migrant_register, name='migrant_register'),
    path('register/success/', views.registration_success, name='registration_success'),
    
    # Status
    path('status/', views.status_check, name='status_check'),
    path('status/', views.status_check, name='check_status'),
    
    # Data
    path('map-data/', views.public_map_data, name='map_data'),
    path('sdg/', views.sdg_dashboard, name='sdg_dashboard'),
    
    # ODK
    path('odk-forms/', views.odk_forms, name='odk_forms'),
    path("data-collection/", views.data_collection_hub, name="data_collection_hub"),
    path("collect/<str:form_type>/", views.collect_form, name="collect_form"),
    path("submissions/", views.submission_list, name="submission_list"),
    path("analytics/", views.analytics_dashboard, name="analytics"),
]
