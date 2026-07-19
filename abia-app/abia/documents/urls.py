from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentCategoryViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r'categories', DocumentCategoryViewSet, basename='documentcategory')
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [path('', include(router.urls))]
