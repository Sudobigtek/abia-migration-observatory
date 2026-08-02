from django.contrib import admin
from abia.geo.models import Hotspot
from abia.accounts.models import LGA

@admin.register(Hotspot)
class HotspotAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['lga']:
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
