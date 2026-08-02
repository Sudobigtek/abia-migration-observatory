from django.contrib import admin
from django.db import models
from abia.search.models import SearchIndex
from abia.accounts.models import LGA

@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['lga_id'] and isinstance(db_field, (models.CharField, models.TextField)):
            from django import forms
            lgas = LGA.objects.values_list('name', flat=True).order_by('name')
            return forms.ChoiceField(choices=[('', '-- Select LGA --')] + [(n, n) for n in lgas])
        return super().formfield_for_dbfield(db_field, request, **kwargs)
