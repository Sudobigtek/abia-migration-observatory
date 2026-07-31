from django.urls import path
from abia.charts import views

app_name = 'charts'
urlpatterns = [
    path('', views.command_center, name='command_center'),
]
