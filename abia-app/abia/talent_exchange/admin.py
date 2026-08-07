from django.contrib import admin
from .models import (
    Sector, Occupation, EmbassyMission, ForeignEmployer, Vacancy,
    TalentPool, Deployment, CredentialEndorsement, WelfareCheck,
    GrievanceTicket, TransparencyReport
)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']

@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'sector', 'experience_years_min', 'is_active']
    list_filter = ['sector', 'is_active']

@admin.register(EmbassyMission)
class EmbassyMissionAdmin(admin.ModelAdmin):
    list_display = ['mission_name', 'country', 'city', 'mission_type', 'mou_signed', 'bla_aligned', 'is_active']
    list_filter = ['mission_type', 'mou_signed', 'bla_aligned', 'is_active']
    search_fields = ['mission_name', 'labour_attache_name']

@admin.register(ForeignEmployer)
class ForeignEmployerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'country', 'city', 'compliance_tier', 'compliance_score', 'embassy_verified', 'active_workers', 'is_active']
    list_filter = ['compliance_tier', 'embassy_verified', 'is_active', 'sector']
    search_fields = ['company_name', 'company_reg', 'city']
    fieldsets = (
        ("Identity", {"fields": (("company_name", "trading_name"), "country", "city", "sector", "company_reg", "website")}),
        ("Contact", {"fields": ("contact_email", "contact_phone")}),
        ("Compliance", {"fields": ("compliance_tier", "compliance_score", "embassy_verified", "verified_by_mission", "verification_date", "contract_compliance_rate")}),
        ("Workers", {"fields": ("total_workers_sourced", "active_workers", "worker_complaints", "avg_salary_usd")}),
        ("Blacklist", {"fields": ("blacklist_reason", "blacklisted_at"), "classes": ("collapse",)}),
        ("System", {"fields": ("is_active", "created_at"), "classes": ("collapse",)}),
    )

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['vacancy_code', 'title', 'employer', 'positions_available', 'positions_filled', 'contract_type', 'salary_usd', 'status']
    list_filter = ['status', 'contract_type', 'occupation__sector']
    search_fields = ['vacancy_code', 'title', 'employer__company_name']

@admin.register(TalentPool)
class TalentPoolAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'lga', 'sector', 'occupation', 'stage', 'assigned_vacancy', 'created_at']
    list_filter = ['stage', 'sector', 'gender', 'is_active']
    search_fields = ['full_name', 'phone', 'email', 'japa_beneficiary_id', 'observatory_person_id']

@admin.register(Deployment)
class DeploymentAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'vacancy', 'deployment_date', 'welfare_status', 'salary_agreed_usd', 'embassy_notified']
    list_filter = ['welfare_status', 'embassy_notified', 'deployment_date']
    date_hierarchy = 'deployment_date'

@admin.register(CredentialEndorsement)
class CredentialEndorsementAdmin(admin.ModelAdmin):
    list_display = ['endorsement_number', 'candidate', 'destination_country', 'purpose', 'issued_date', 'valid_until', 'is_revoked']
    list_filter = ['purpose', 'is_revoked', 'issued_date']
    readonly_fields = ['verification_hash', 'issued_date']

@admin.register(WelfareCheck)
class WelfareCheckAdmin(admin.ModelAdmin):
    list_display = ['deployment', 'check_date', 'check_type', 'salary_paid_on_time', 'accommodation_acceptable', 'escalated_to_embassy']
    list_filter = ['check_type', 'salary_paid_on_time', 'escalated_to_embassy']

@admin.register(GrievanceTicket)
class GrievanceTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'deployment', 'category', 'severity', 'status', 'reported_date']
    list_filter = ['severity', 'status', 'category']

@admin.register(TransparencyReport)
class TransparencyReportAdmin(admin.ModelAdmin):
    list_display = ['snapshot_date', 'period_type', 'year', 'quarter', 'workers_deployed_total', 'employers_verified', 'endorsements_issued']
    list_filter = ['period_type', 'year']
