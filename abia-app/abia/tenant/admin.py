from django.contrib import admin
from abia.tenant.models import TenantRole
from abia.accounts.models import LGA

@admin.register(TenantRole)
class TenantRoleAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['lga']:
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
