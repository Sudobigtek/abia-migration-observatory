from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DynamicFieldDefinitionViewSet, EntityDynamicDataViewSet

router = DefaultRouter()
router.register(r'definitions', DynamicFieldDefinitionViewSet)
router.register(r'data', EntityDynamicDataViewSet)

urlpatterns = [path('', include(router.urls))]
