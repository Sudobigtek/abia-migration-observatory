from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class CertifiedVolunteer(models.Model):
    STATUS_CHOICES = [
        ('applicant', 'Applicant'), ('in_training', 'In Training'),
        ('certified', 'Certified'), ('suspended', 'Suspended'),
        ('decertified', 'Decertified'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    photograph = models.ImageField(upload_to='corps/photos/', blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    lga = models.CharField(max_length=100)
    town_union = models.CharField(max_length=200)
    proof_document = models.FileField(upload_to='corps/proofs/', blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applicant')
    certification_number = models.CharField(max_length=50, unique=True, blank=True)
    authority_letter_issued = models.BooleanField(default=False)
    authority_letter_valid_until = models.DateField(null=True, blank=True)
    qr_code_verification = models.CharField(max_length=200, blank=True)
    deployment_country = models.CharField(max_length=100, blank=True)
    deployment_city = models.CharField(max_length=100, blank=True)
    hours_served_monthly = models.PositiveIntegerField(default=0)
    hours_served_total = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    assigned_slo = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='slo_volunteers')
    institute_student_id = models.CharField(max_length=50, blank=True, help_text="Link to Institute StudentEnrollment")
    referee_diaspora_assoc = models.CharField(max_length=200, blank=True)
    referee_town_union = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Certified Volunteer'
        verbose_name_plural = 'Certified Volunteers'

    @property
    def full_name(self):
        return f"{self.first_name} {self.other_names} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} ({self.country})"

class CountryCluster(models.Model):
    REGION_CHOICES = [
        ('europe_americas', 'Europe & the Americas'),
        ('africa_middle_east', 'Africa & the Middle East'),
        ('asia_oceania', 'Asia & Oceania'),
    ]
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    coordinator = models.ForeignKey(CertifiedVolunteer, on_delete=models.SET_NULL, null=True, blank=True, related_name='clusters_coordinated')
    volunteers = models.ManyToManyField(CertifiedVolunteer, blank=True, related_name='clusters')
    active_status = models.BooleanField(default=True)
    monthly_report_due = models.PositiveIntegerField(default=1)
    class Meta:
        unique_together = ['country', 'city']
        ordering = ['country', 'city']
        verbose_name = 'Country Cluster'
        verbose_name_plural = 'Country Clusters'
    def __str__(self):
        return f"{self.city}, {self.country}" if self.city else self.country

class CorpsLeadership(models.Model):
    ROLE_CHOICES = [
        ('president', 'President'),
        ('vp_europe_americas', 'VP — Europe & Americas'),
        ('vp_africa_middle_east', 'VP — Africa & Middle East'),
        ('vp_asia_oceania', 'VP — Asia & Oceania'),
        ('secretary_general', 'Secretary-General'),
        ('treasurer', 'Treasurer'),
        ('ethics_chair', 'Chair — Ethics & Disciplinary'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    volunteer = models.ForeignKey(CertifiedVolunteer, on_delete=models.CASCADE, related_name='leadership_roles')
    term_start = models.DateField()
    term_end = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['role']
        verbose_name = 'Leadership Position'
        verbose_name_plural = 'Leadership Positions'
    def __str__(self):
        return f"{self.get_role_display()} — {self.volunteer.full_name}"

class WelfareContact(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('welcome_orientation', 'Welcome & Orientation'),
        ('welfare_check', 'Welfare Monitoring'),
        ('info_guidance', 'Information & Guidance'),
        ('referral', 'Referral Service'),
        ('crisis_response', 'Crisis Response'),
        ('community_building', 'Community Building'),
        ('circular_migration', 'Circular Migration Promotion'),
    ]
    volunteer = models.ForeignKey(CertifiedVolunteer, on_delete=models.CASCADE, related_name='welfare_contacts')
    migrant_name = models.CharField(max_length=200, blank=True)
    migrant_phone = models.CharField(max_length=20, blank=True)
    migrant_email = models.EmailField(blank=True)
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES)
    description = models.TextField()
    referral_made = models.BooleanField(default=False)
    referral_to = models.CharField(max_length=200, blank=True)
    follow_up_required = models.BooleanField(default=False)
    contact_date = models.DateField()
    anonymised_data_submitted = models.BooleanField(default=False)
    observatory_person_id = models.CharField(max_length=50, blank=True, help_text="Link to Observatory Migrant")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-contact_date']
        verbose_name = 'Welfare Contact'
        verbose_name_plural = 'Welfare Contacts'

class ActivityLog(models.Model):
    volunteer = models.ForeignKey(CertifiedVolunteer, on_delete=models.CASCADE, related_name='activity_logs')
    month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.PositiveIntegerField()
    hours_served = models.PositiveIntegerField(default=0)
    migrants_contacted_count = models.PositiveIntegerField(default=0)
    welfare_checks_count = models.PositiveIntegerField(default=0)
    referrals_made_count = models.PositiveIntegerField(default=0)
    community_events_count = models.PositiveIntegerField(default=0)
    report_submitted_at = models.DateTimeField(auto_now_add=True)
    slo_reviewed_at = models.DateTimeField(null=True, blank=True)
    slo_feedback = models.TextField(blank=True)
    class Meta:
        unique_together = ['volunteer', 'month', 'year']
        ordering = ['-year', '-month']
        verbose_name = 'Monthly Activity Log'
        verbose_name_plural = 'Monthly Activity Logs'

class EthicsComplaint(models.Model):
    TYPE_CHOICES = [
        ('confidentiality_breach', 'Breach of Confidentiality'),
        ('exploitation', 'Exploitation or Harm'),
        ('impersonation', 'Impersonation or False Representation'),
        ('political_partisan', 'Political Partisan Activity'),
        ('fraud', 'Fraud or Embezzlement'),
        ('misconduct', 'General Misconduct'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('appealed', 'Appealed to IMGP'),
    ]
    REC_CHOICES = [
        ('warning', 'Written Warning'),
        ('suspension', 'Suspension'),
        ('decertification', 'Decertification'),
        ('law_enforcement', 'Referral to Law Enforcement'),
    ]
    complainant_name = models.CharField(max_length=200)
    complainant_contact = models.CharField(max_length=200, blank=True)
    respondent = models.ForeignKey(CertifiedVolunteer, on_delete=models.CASCADE, related_name='ethics_complaints')
    complaint_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    description = models.TextField()
    evidence = models.FileField(upload_to='corps/ethics/', blank=True)
    committee_findings = models.TextField(blank=True)
    recommendation = models.CharField(max_length=30, choices=REC_CHOICES, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    appeal_to_imgp = models.BooleanField(default=False)
    imgp_decision = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateField(null=True, blank=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ethics Complaint'
        verbose_name_plural = 'Ethics Complaints'

class TrainingModule(models.Model):
    module_number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    pass_mark = models.PositiveIntegerField(default=80)
    institute_course_code = models.CharField(max_length=20, blank=True, help_text="Link to Institute CourseCatalog code")
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['module_number']
        verbose_name = 'Training Module'
        verbose_name_plural = 'Training Modules'
    def __str__(self):
        return f"Module {self.module_number}: {self.title}"

class VolunteerTrainingProgress(models.Model):
    volunteer = models.ForeignKey(CertifiedVolunteer, on_delete=models.CASCADE, related_name='training_progress')
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='progress_records')
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    passed = models.BooleanField(default=False)
    class Meta:
        unique_together = ['volunteer', 'module']
        verbose_name = 'Training Progress'
        verbose_name_plural = 'Training Progress Records'

class DiasporaPartner(models.Model):
    association_name = models.CharField(max_length=300)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=200)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    letter_of_cooperation_signed = models.BooleanField(default=False)
    signed_date = models.DateField(null=True, blank=True)
    nominated_volunteers_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['association_name']
        verbose_name = 'Diaspora Partner'
        verbose_name_plural = 'Diaspora Partners'
    def __str__(self):
        return self.association_name
