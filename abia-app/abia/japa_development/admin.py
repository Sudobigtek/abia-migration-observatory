
from django.contrib import admin
from .models import Beneficiary, PillarParticipation, ProgramOutcomeSnapshot, PolicyEvidence, StakeholderEngagement

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ["full_name", "gender", "age", "lga", "baseline_status", "current_status", "current_location_category", "skill_sector", "enrolled_date", "is_active"]
    list_filter = ["gender", "current_status", "current_location_category", "skill_sector", "baseline_status", "lga", "is_active"]
    search_fields = ["first_name", "last_name", "phone", "email", "observatory_person_id"]
    date_hierarchy = "enrolled_date"
    readonly_fields = ["created_at", "updated_at", "age"]
    fieldsets = (
        ("Identity", {"fields": ("first_name", "last_name", "other_names", "phone", "email", "date_of_birth", "gender")}),
        ("Location", {"fields": ("lga", "ward", "community")}),
        ("Baseline & Status", {"fields": ("education_level", "baseline_status", "current_status", "status_changed_at", "notes")}),
        ("Skills Inventory", {"fields": ("primary_skill", "secondary_skill", "skill_sector", "years_of_experience")}),
        ("Current Location", {"fields": ("current_location_category", "current_country", "current_state", "current_city")}),
        ("Economic Opt-in", {"fields": ("monthly_remittance_ngn", "remittance_frequency", "willing_to_invest", "willing_to_mentor", "willing_to_return", "willing_to_volunteer"), "classes": ("collapse",)}),
        ("Observatory Link", {"fields": ("observatory_person_id",), "classes": ("collapse",)}),
        ("System", {"fields": ("created_at", "updated_at", "is_active"), "classes": ("collapse",)}),
    )

@admin.register(PillarParticipation)
class PillarParticipationAdmin(admin.ModelAdmin):
    list_display = ["beneficiary", "pillar", "enrolled_date", "completed_date", "placement_status", "certification_issued", "micro_enterprise_registered"]
    list_filter = ["pillar", "dropout_reason", "placement_status", "certification_issued", "migration_pathway", "protection_referral_made"]
    search_fields = ["beneficiary__first_name", "beneficiary__last_name", "destination_country", "training_sector"]
    date_hierarchy = "enrolled_date"
    raw_id_fields = ["beneficiary"]
    fieldsets = (
        ("Enrollment", {"fields": ("beneficiary", "pillar", "enrolled_date", "completed_date", "dropped_out", "dropout_reason")}),
        ("Pillar 1 — Governance", {"fields": ("counseling_sessions_attended", "total_counseling_sessions", "migration_pathway", "destination_country", "trafficking_vulnerability_baseline", "trafficking_vulnerability_exit", "protection_referral_made", "protection_referral_date"), "classes": ("collapse",)}),
        ("Pillar 2 — Language", {"fields": ("language_course", "language_proficiency_baseline", "language_proficiency_exit", "cultural_orientation_modules", "cultural_orientation_completed", "integration_readiness_score"), "classes": ("collapse",)}),
        ("Pillar 3 — Skills", {"fields": ("training_sector", "training_hours_completed", "training_hours_total", "certification_issued", "certification_type", "certification_body", "certification_date", "skills_market_alignment_score", "placement_status", "placement_employer", "placement_date", "placement_salary_ngn"), "classes": ("collapse",)}),
        ("Pillar 4 — Reintegration", {"fields": ("returnee_needs_assessment", "reintegration_package_type", "reintegration_package_value_ngn", "reintegration_package_delivered", "reintegration_package_date", "business_incubation_enrolled", "mentor_assigned", "micro_enterprise_registered", "business_cac_number", "business_sector", "business_employees", "alumni_network_member", "alumni_engagement_count"), "classes": ("collapse",)}),
    )

@admin.register(ProgramOutcomeSnapshot)
class ProgramOutcomeSnapshotAdmin(admin.ModelAdmin):
    list_display = ["__str__", "period_type", "total_budget_period", "total_spent_period", "utilization_rate", "cost_per_beneficiary", "created_at"]
    list_filter = ["period_type", "year", "quarter"]
    readonly_fields = ["created_at", "updated_at", "utilization_rate", "cost_per_beneficiary"]
    fieldsets = (
        ("Period", {"fields": ("snapshot_date", "period_type", "year", "quarter", "month")}),
        ("Pillar 1 Metrics", {"fields": ("p1_counseled_total", "p1_counseled_target", "p1_regular_pathway_uptake", "p1_irregular_pathway_uptake", "p1_trafficking_referrals", "p1_info_sessions_held", "p1_materials_distributed", "p1_spent"), "classes": ("collapse",)}),
        ("Pillar 2 Metrics", {"fields": ("p2_language_enrolled_total", "p2_cultural_orientation_completed", "p2_avg_integration_readiness", "p2_spent"), "classes": ("collapse",)}),
        ("Pillar 3 Metrics", {"fields": ("p3_trained_total", "p3_trained_target", "p3_certifications_issued", "p3_placed_employed", "p3_placed_self_employed", "p3_placed_abroad", "p3_unemployed", "p3_spent"), "classes": ("collapse",)}),
        ("Pillar 4 Metrics", {"fields": ("p4_returnees_supported", "p4_returnees_target", "p4_reintegration_packages", "p4_micro_enterprises", "p4_micro_enterprises_target", "p4_businesses_surviving_6mo", "p4_businesses_surviving_12mo", "p4_alumni_active", "p4_spent"), "classes": ("collapse",)}),
        ("Finance & Demographics", {"fields": ("total_budget_period", "total_spent_period", "count_abia", "count_se_other", "count_other_ng", "count_abroad", "count_male", "count_female", "count_other_gender"), "classes": ("collapse",)}),
        ("System", {"fields": ("created_at", "updated_at", "generated_by"), "classes": ("collapse",)}),
    )

@admin.register(PolicyEvidence)
class PolicyEvidenceAdmin(admin.ModelAdmin):
    list_display = ["title", "pillar_focus", "submitted_to", "submission_date", "is_published", "created_at"]
    list_filter = ["pillar_focus", "is_published", "submission_date"]
    search_fields = ["title", "description", "key_findings", "submitted_to"]
    date_hierarchy = "created_at"

@admin.register(StakeholderEngagement)
class StakeholderEngagementAdmin(admin.ModelAdmin):
    list_display = ["partner", "activity_type", "engagement_date", "beneficiaries_reached", "value_ngn", "follow_up_required"]
    list_filter = ["partner", "activity_type", "pillar", "follow_up_required"]
    search_fields = ["description", "follow_up_notes", "partner_other"]
    date_hierarchy = "engagement_date"


from .models import ProgramSession, Attendance, Facilitator, TrainingInventory

@admin.register(ProgramSession)
class ProgramSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'pillar_participation', 'session_date', 'start_time', 'facilitator', 'status', 'max_participants']
    list_filter = ['status', 'session_date', 'pillar_participation__pillar']
    search_fields = ['title', 'venue', 'facilitator']
    date_hierarchy = 'session_date'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['beneficiary', 'session', 'status', 'participation_score', 'check_in_time']
    list_filter = ['status', 'session__session_date']
    search_fields = ['beneficiary__first_name', 'beneficiary__last_name', 'session__title']
    raw_id_fields = ['beneficiary', 'session']

@admin.register(Facilitator)
class FacilitatorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'facilitator_type', 'organization', 'is_active']
    list_filter = ['facilitator_type', 'is_active']
    search_fields = ['full_name', 'email', 'organization']

@admin.register(TrainingInventory)
class TrainingInventoryAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'quantity_on_hand', 'quantity_issued', 'unit_cost_ngn', 'needs_reorder', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['item_name', 'supplier', 'location']
