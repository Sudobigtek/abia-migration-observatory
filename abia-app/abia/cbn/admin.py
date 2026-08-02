from django.contrib import admin
from abia.cbn.models import RemittanceRecord
from abia.accounts.models import LGA

@admin.register(RemittanceRecord)
class RemittanceRecordAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['recipient_lga']:
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
