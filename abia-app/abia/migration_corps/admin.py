from django.contrib import admin
from .models import (CertifiedVolunteer, CountryCluster, CorpsLeadership,
    WelfareContact, ActivityLog, EthicsComplaint, TrainingModule,
    VolunteerTrainingProgress, DiasporaPartner)

@admin.register(CertifiedVolunteer)
class CertifiedVolunteerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'country', 'city', 'status', 'certification_number', 'hours_served_total', 'is_active']
    list_filter = ['status', 'gender', 'country', 'is_active', 'authority_letter_issued']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'certification_number', 'institute_student_id']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'full_name']
    fieldsets = (
        ("Identity", {"fields": (("first_name", "last_name", "other_names"), "date_of_birth", "gender", "photograph")}),
        ("Contact", {"fields": ("email", "phone", "whatsapp")}),
        ("Origin", {"fields": ("lga", "town_union", "proof_document")}),
        ("Residence", {"fields": ("country", "city", "address")}),
        ("Certification", {"fields": ("status", "certification_number", "authority_letter_issued", "authority_letter_valid_until", "qr_code_verification")}),
        ("Deployment", {"fields": ("deployment_country", "deployment_city", "hours_served_monthly", "hours_served_total", "last_activity_date")}),
        ("Supervision", {"fields": ("assigned_slo", "institute_student_id")}),
        ("Referees", {"fields": ("referee_diaspora_assoc", "referee_town_union"), "classes": ("collapse",)}),
        ("System", {"fields": ("created_at", "updated_at", "is_active"), "classes": ("collapse",)}),
    )

@admin.register(CountryCluster)
class CountryClusterAdmin(admin.ModelAdmin):
    list_display = ['country', 'city', 'region', 'coordinator', 'active_status']
    list_filter = ['region', 'active_status']
    search_fields = ['country', 'city']
    filter_horizontal = ['volunteers']

@admin.register(CorpsLeadership)
class CorpsLeadershipAdmin(admin.ModelAdmin):
    list_display = ['role', 'volunteer', 'term_start', 'term_end', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['volunteer__first_name', 'volunteer__last_name']

@admin.register(WelfareContact)
class WelfareContactAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'contact_type', 'contact_date', 'referral_made', 'follow_up_required', 'anonymised_data_submitted']
    list_filter = ['contact_type', 'referral_made', 'follow_up_required', 'contact_date']
    search_fields = ['migrant_name', 'description']
    date_hierarchy = 'contact_date'

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'month', 'year', 'hours_served', 'migrants_contacted_count', 'slo_reviewed_at']
    list_filter = ['year', 'month']
    search_fields = ['volunteer__first_name', 'volunteer__last_name']

@admin.register(EthicsComplaint)
class EthicsComplaintAdmin(admin.ModelAdmin):
    list_display = ['respondent', 'complaint_type', 'status', 'recommendation', 'created_at', 'appeal_to_imgp']
    list_filter = ['complaint_type', 'status', 'recommendation']
    search_fields = ['complainant_name', 'description']
    date_hierarchy = 'created_at'

@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ['module_number', 'title', 'pass_mark', 'institute_course_code', 'is_active']
    search_fields = ['title', 'institute_course_code']

@admin.register(VolunteerTrainingProgress)
class VolunteerTrainingProgressAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'module', 'completed_at', 'score', 'passed']
    list_filter = ['passed', 'module']

@admin.register(DiasporaPartner)
class DiasporaPartnerAdmin(admin.ModelAdmin):
    list_display = ['association_name', 'country', 'city', 'letter_of_cooperation_signed', 'is_active']
    list_filter = ['letter_of_cooperation_signed', 'is_active']
    search_fields = ['association_name', 'contact_person']
