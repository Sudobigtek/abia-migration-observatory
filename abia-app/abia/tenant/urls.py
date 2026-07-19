from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantRoleViewSet, my_permissions

router = DefaultRouter()
router.register(r"roles", TenantRoleViewSet, basename="tenantrole")

urlpatterns = [
    path("", include(router.urls)),
    path("my-permissions/", my_permissions, name="tenant-my-permissions"),
]