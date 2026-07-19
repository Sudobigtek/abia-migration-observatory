from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IPFSDocumentViewSet, PinQueueViewSet

router = DefaultRouter()
router.register(r'documents', IPFSDocumentViewSet)
router.register(r'pin-queue', PinQueueViewSet)

urlpatterns = [path('', include(router.urls))]
