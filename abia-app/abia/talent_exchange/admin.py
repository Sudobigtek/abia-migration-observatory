from django.contrib import admin
from .models import (
    Sector, Occupation, EmbassyMission, ForeignEmployer,
    Vacancy, TalentPool, Deployment, CredentialEndorsement,
    WelfareCheck, GrievanceTicket, TransparencyReport
)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']

@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'sector', 'experience_years_min']
    list_filter = ['sector']
    search_fields = ['code', 'title']

@admin.register(EmbassyMission)
class EmbassyMissionAdmin(admin.ModelAdmin):
    list_display = ['mission_name', 'country', 'city', 'mou_signed', 'bla_aligned']
    list_filter = ['mou_signed', 'bla_aligned', 'mission_type']
    search_fields = ['mission_name', 'country', 'city']

@admin.register(ForeignEmployer)
class ForeignEmployerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'country', 'compliance_tier', 'compliance_score', 'embassy_verified', 'is_blacklisted', 'is_active']
    list_filter = ['compliance_tier', 'embassy_verified', 'is_blacklisted', 'is_active']
    search_fields = ['company_name', 'country', 'company_reg']

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['vacancy_code', 'title', 'employer', 'occupation', 'status', 'positions_available', 'positions_filled']
    list_filter = ['status', 'contract_type']
    search_fields = ['vacancy_code', 'title']

@admin.register(TalentPool)
class TalentPoolAdmin(admin.ModelAdmin):
    list_display = ['japa_beneficiary_id', 'full_name', 'lga', 'sector', 'stage', 'is_active']
    list_filter = ['stage', 'sector', 'is_active']
    search_fields = ['full_name', 'japa_beneficiary_id', 'email']

@admin.register(Deployment)
class DeploymentAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'vacancy', 'deployment_date', 'welfare_status', 'embassy_notified']
    list_filter = ['welfare_status', 'embassy_notified']
    search_fields = ['candidate__full_name', 'vacancy__title']

@admin.register(CredentialEndorsement)
class CredentialEndorsementAdmin(admin.ModelAdmin):
    list_display = ['endorsement_number', 'candidate', 'destination_country', 'purpose', 'is_revoked', 'valid_until']
    list_filter = ['purpose', 'is_revoked', 'destination_country']
    search_fields = ['endorsement_number', 'candidate__full_name']

@admin.register(WelfareCheck)
class WelfareCheckAdmin(admin.ModelAdmin):
    list_display = ['deployment', 'check_date', 'check_type', 'salary_paid_on_time', 'accommodation_acceptable']
    list_filter = ['check_type', 'salary_paid_on_time', 'accommodation_acceptable']

@admin.register(GrievanceTicket)
class GrievanceTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'deployment', 'category', 'status']
    list_filter = ['category', 'status']
    search_fields = ['ticket_number', 'deployment__candidate__full_name']

@admin.register(TransparencyReport)
class TransparencyReportAdmin(admin.ModelAdmin):
    list_display = ['snapshot_date', 'period_type', 'year', 'quarter', 'workers_deployed_total']
    list_filter = ['period_type', 'year']

