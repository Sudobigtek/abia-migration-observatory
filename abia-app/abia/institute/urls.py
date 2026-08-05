from django.urls import path
from . import views

app_name = 'institute'

urlpatterns = [
    path('', views.institute_dashboard, name='dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('verify/', views.verify_certificate, name='verify_certificate'),
]
