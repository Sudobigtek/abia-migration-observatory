from django.contrib import admin
from .models import MapLayer

@admin.register(MapLayer)
class MapLayerAdmin(admin.ModelAdmin):
    list_display = ["name", "layer_type", "is_visible", "is_public", "z_index", "created_by", "created_at"]
    list_filter = ["layer_type", "is_visible", "is_public", "created_at"]
    search_fields = ["name", "description"]