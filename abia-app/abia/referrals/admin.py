from django.contrib import admin
from .models import Referral

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['case', 'from_lga', 'to_lga', 'to_organization', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reason', 'to_contact_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
