from django.contrib import admin
from django.db import models
from .models import (
    VictimIntake, Shelter, ShelterStay, Perpetrator, CourtCase,
    Evidence, PsychosocialSession, ReintegrationPlan,
    CommunityAwarenessEvent, SchoolProgram, FakeJobAlert,
    MissingPerson, FamilyReunification,
)
from abia.accounts.models import LGA


@admin.register(VictimIntake)
class VictimIntakeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'age', 'gender', 'status', 'lga_of_origin', 'intake_date', 'synced_to_naptip']
    list_filter = ['status', 'exploitation_type', 'gender', 'intake_date', 'synced_to_naptip']
    search_fields = ['full_name', 'phone', 'trafficking_route']
    date_hierarchy = 'intake_date'
    list_per_page = 25

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('lga_of_origin', 'current_lga'):
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            lga = request.user.userprofile.assigned_lga
            if lga:
                return qs.filter(current_lga__name=lga)
        except Exception:
            pass
        return qs


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ['name', 'lga', 'capacity', 'current_occupancy', 'available_beds', 'is_active']
    list_filter = ['is_active', 'lga']
    search_fields = ['name', 'address']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'lga':
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ShelterStay)
class ShelterStayAdmin(admin.ModelAdmin):
    list_display = ['victim', 'shelter', 'date_admitted', 'date_discharged']
    list_filter = ['shelter', 'date_admitted']


@admin.register(Perpetrator)
class PerpetratorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'risk_level', 'lga_of_operation', 'is_active', 'created_at']
    list_filter = ['risk_level', 'is_active', 'gender']
    search_fields = ['full_name', 'aliases', 'phone_numbers']
    date_hierarchy = 'created_at'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'lga_of_operation':
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm('anti_trafficking.view_perpetrator_database'):
            return qs
        return qs.none()


@admin.register(CourtCase)
class CourtCaseAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'victim', 'perpetrator', 'status', 'next_hearing_date', 'court_name']
    list_filter = ['status', 'prosecution_agency', 'next_hearing_date']
    search_fields = ['case_number', 'charges', 'victim__full_name']
    date_hierarchy = 'next_hearing_date'


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ['case', 'evidence_type', 'collected_at', 'ipfs_hash']
    list_filter = ['evidence_type', 'collected_at']


@admin.register(PsychosocialSession)
class PsychosocialSessionAdmin(admin.ModelAdmin):
    list_display = ['victim', 'session_date', 'counselor', 'trauma_score', 'next_session_date']
    list_filter = ['session_date', 'counselor']


@admin.register(ReintegrationPlan)
class ReintegrationPlanAdmin(admin.ModelAdmin):
    list_display = ['victim', 'status', 'family_reunification_status', 'business_status']
    list_filter = ['status', 'business_status']


@admin.register(CommunityAwarenessEvent)
class CommunityAwarenessEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'lga', 'date', 'attendance_count']
    list_filter = ['event_type', 'lga', 'date']
    date_hierarchy = 'date'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'lga':
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(SchoolProgram)
class SchoolProgramAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'lga', 'program_date', 'students_reached', 'peer_educators_trained']
    list_filter = ['lga', 'program_date']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'lga':
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(FakeJobAlert)
class FakeJobAlertAdmin(admin.ModelAdmin):
    list_display = ['agency_name', 'lga', 'status', 'promised_job', 'created_at']
    list_filter = ['status', 'lga', 'created_at']
    search_fields = ['agency_name', 'contact_person']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'lga':
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(MissingPerson)
class MissingPersonAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'age', 'status', 'lga', 'last_seen_date', 'matched_victim']
    list_filter = ['status', 'gender', 'last_seen_date']
    search_fields = ['full_name', 'last_seen_location']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'lga':
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(FamilyReunification)
class FamilyReunificationAdmin(admin.ModelAdmin):
    list_display = ['victim', 'family_contact_name', 'family_lga', 'reunification_date', 'is_safe_placement']
    list_filter = ['is_safe_placement', 'dna_test_status']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'family_lga':
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
