from django.contrib import admin
from .models import CourseCatalog, Cohort, StudentEnrollment, ExamSchedule, PartnerInstitution, CertificateVerification

@admin.register(CourseCatalog)
class CourseCatalogAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'level', 'duration_hours', 'delivery_mode', 'is_accredited', 'is_active']
    list_filter = ['level', 'delivery_mode', 'sector', 'is_accredited', 'is_active']
    search_fields = ['code', 'title', 'accreditation_body']

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ['course', 'cohort_number', 'start_date', 'end_date', 'status', 'max_students', 'facilitator']
    list_filter = ['status', 'start_date', 'course__sector']
    search_fields = ['course__title', 'facilitator', 'venue']
    date_hierarchy = 'start_date'

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'cohort', 'status', 'final_score', 'certificate_issued', 'certificate_number', 'enrollment_date']
    list_filter = ['status', 'certificate_issued', 'enrollment_date']
    search_fields = ['full_name', 'email', 'phone', 'certificate_number', 'japa_beneficiary_id']
    date_hierarchy = 'enrollment_date'

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ['exam_title', 'cohort', 'exam_date', 'start_time', 'duration_minutes', 'venue']
    list_filter = ['exam_date']
    search_fields = ['exam_title', 'venue']
    date_hierarchy = 'exam_date'

@admin.register(PartnerInstitution)
class PartnerInstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution_type', 'location', 'mou_signed', 'is_active']
    list_filter = ['institution_type', 'mou_signed', 'is_active']
    search_fields = ['name', 'contact_person', 'location']
    filter_horizontal = ['courses_offered']

@admin.register(CertificateVerification)
class CertificateVerificationAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'student_name', 'course_title', 'issue_date', 'is_valid', 'verified_count']
    list_filter = ['is_valid', 'issue_date']
    search_fields = ['certificate_number', 'student_name', 'course_title']
    date_hierarchy = 'issue_date'
