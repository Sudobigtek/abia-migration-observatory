from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowDefinitionViewSet, WorkflowInstanceViewSet

router = DefaultRouter()
router.register(r'definitions', WorkflowDefinitionViewSet, basename='workflowdefinition')
router.register(r'instances', WorkflowInstanceViewSet, basename='workflowinstance')

urlpatterns = [path('', include(router.urls))]
