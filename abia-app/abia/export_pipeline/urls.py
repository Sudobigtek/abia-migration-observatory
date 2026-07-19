from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataExportViewSet

router = DefaultRouter()
router.register(r"exports", DataExportViewSet, basename="dataexport")

urlpatterns = [
    path("", include(router.urls)),
]
