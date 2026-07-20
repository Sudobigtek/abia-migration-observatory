from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImportJobViewSet, upload_csv, import_template

router = DefaultRouter()
router.register(r"jobs", ImportJobViewSet, basename="importjob")

urlpatterns = [
    path("", include(router.urls)),
    path("upload/", upload_csv, name="importer-upload"),
    path("template/<str:entity_type>/", import_template, name="importer-template"),
]