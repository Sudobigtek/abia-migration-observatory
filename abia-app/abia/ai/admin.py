from django.contrib import admin
from .models import RiskAssessment

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['migrant', 'risk_score', 'risk_level', 'created_at']
    list_filter = ['risk_level', 'created_at']
    search_fields = ['migrant__full_name']
