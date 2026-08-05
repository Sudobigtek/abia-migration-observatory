from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CourseCatalog(models.Model):
    LEVEL_CHOICES = [
        ('basic', 'Basic / Introductory'), ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'), ('diploma', 'Diploma'),
        ('professional', 'Professional Certification'),
    ]
    DELIVERY_CHOICES = [
        ('in_person', 'In-Person'), ('online', 'Online'),
        ('hybrid', 'Hybrid'), ('self_paced', 'Self-Paced'),
    ]

    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=300)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    duration_hours = models.PositiveIntegerField()
    delivery_mode = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    sector = models.CharField(max_length=100, blank=True, choices=[
        ('health', 'Health'), ('tech', 'Technology'), ('trades', 'Trades'),
        ('agriculture', 'Agriculture'), ('business', 'Business'), ('creative', 'Creative Arts'),
    ])
    learning_outcomes = models.TextField(blank=True)
    prerequisites = models.TextField(blank=True)
    is_accredited = models.BooleanField(default=False)
    accreditation_body = models.CharField(max_length=200, blank=True)
    partner_institution = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f"{self.code}: {self.title}"

class Cohort(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'), ('enrolling', 'Open for Enrollment'),
        ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled'),
    ]

    course = models.ForeignKey(CourseCatalog, on_delete=models.CASCADE, related_name='cohorts')
    cohort_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    facilitator = models.CharField(max_length=200, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    max_students = models.PositiveIntegerField(default=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    japa_program_session = models.CharField(max_length=50, blank=True, help_text="Link to japa_development.ProgramSession ID if cross-referenced")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['course', 'cohort_number']
        ordering = ['-start_date']
        verbose_name = 'Cohort'
        verbose_name_plural = 'Cohorts'

    def __str__(self):
        return f"{self.course.code} — Cohort {self.cohort_number}"

class StudentEnrollment(models.Model):
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'), ('active', 'Active'),
        ('completed', 'Completed'), ('dropped', 'Dropped'), ('suspended', 'Suspended'),
    ]

    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='enrollments')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    lga = models.CharField(max_length=100, blank=True)
    japa_beneficiary_id = models.CharField(max_length=50, blank=True, help_text="Link to japa_development.Beneficiary")
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    final_score = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    certificate_issued = models.BooleanField(default=False)
    certificate_number = models.CharField(max_length=50, blank=True, unique=True)
    certificate_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['cohort', 'full_name', 'phone']
        ordering = ['-enrollment_date']
        verbose_name = 'Student Enrollment'
        verbose_name_plural = 'Student Enrollments'

    def __str__(self):
        return f"{self.full_name} — {self.cohort}"

class ExamSchedule(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='exams')
    exam_title = models.CharField(max_length=200)
    exam_date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=120)
    venue = models.CharField(max_length=200, blank=True)
    max_score = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-exam_date']
        verbose_name = 'Exam Schedule'
        verbose_name_plural = 'Exam Schedules'

    def __str__(self):
        return f"{self.exam_title} ({self.exam_date})"

class PartnerInstitution(models.Model):
    TYPE_CHOICES = [
        ('polytechnic', 'Polytechnic'), ('university', 'University'),
        ('vocational', 'Vocational Center'), ('ngo', 'NGO / CSO'),
        ('private', 'Private Sector'), ('government', 'Government Agency'),
        ('international', 'International Organization'),
    ]

    name = models.CharField(max_length=300)
    institution_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    mou_signed = models.BooleanField(default=False)
    mou_date = models.DateField(null=True, blank=True)
    courses_offered = models.ManyToManyField(CourseCatalog, blank=True, related_name='partner_institutions')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Partner Institution'
        verbose_name_plural = 'Partner Institutions'

    def __str__(self):
        return self.name

class CertificateVerification(models.Model):
    certificate_number = models.CharField(max_length=50, unique=True)
    student_name = models.CharField(max_length=200)
    course_title = models.CharField(max_length=300)
    issue_date = models.DateField()
    accredited_by = models.CharField(max_length=200, blank=True)
    is_valid = models.BooleanField(default=True)
    revocation_reason = models.TextField(blank=True)
    verified_count = models.PositiveIntegerField(default=0)
    last_verified = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Certificate Record'
        verbose_name_plural = 'Certificate Records'

    def __str__(self):
        return f"{self.certificate_number} — {self.student_name}"
