
""" Japa for Development — Program M&E Tracker
Aligned to IOM M&E Guidelines, JLMP Framework, GCM Indicators """
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Beneficiary(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"), ("female", "Female"), ("other", "Other"), ("prefer_not", "Prefer not to say"),
    ]
    BASELINE_STATUS_CHOICES = [
        ("unemployed", "Unemployed"), ("student", "Student"), ("employed", "Employed"),
        ("self_employed", "Self-employed"), ("migrant_abroad", "Migrant Abroad"),
        ("returnee", "Returnee"), ("aspiring_migrant", "Aspiring Migrant"),
    ]
    CURRENT_STATUS_CHOICES = [
        ("active", "Active in Program"), ("completed_training", "Completed Training"),
        ("migrated_regular", "Migrated — Regular Pathway"), ("migrated_irregular", "Migrated — Irregular Pathway"),
        ("employed_local", "Employed Locally"), ("self_employed_local", "Self-employed Locally"),
        ("returned", "Returned"), ("reintegrated", "Reintegrated"), ("dropped_out", "Dropped Out"),
    ]
    LOCATION_CHOICES = [
        ("abia", "Abia State"), ("se_other", "Other South East"),
        ("other_ng", "Other Nigeria"), ("abroad", "Abroad"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    lga = models.CharField(max_length=100, verbose_name="LGA (Abia State)")
    ward = models.CharField(max_length=100, blank=True)
    community = models.CharField(max_length=200, blank=True)
    education_level = models.CharField(max_length=50, blank=True)
    baseline_status = models.CharField(max_length=20, choices=BASELINE_STATUS_CHOICES, default="aspiring_migrant")
    primary_skill = models.CharField(max_length=200, blank=True)
    secondary_skill = models.CharField(max_length=200, blank=True)
    skill_sector = models.CharField(max_length=100, blank=True, choices=[
        ("health", "Health"), ("tech", "Technology & Digital"), ("trades", "Trades & Manufacturing"),
        ("agriculture", "Agriculture"), ("education", "Education"), ("business", "Business & Entrepreneurship"),
        ("creative", "Creative Arts"), ("other", "Other"),
    ])
    years_of_experience = models.PositiveIntegerField(default=0)
    enrolled_date = models.DateField(auto_now_add=True)
    current_status = models.CharField(max_length=20, choices=CURRENT_STATUS_CHOICES, default="active")
    status_changed_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    current_location_category = models.CharField(max_length=20, choices=LOCATION_CHOICES, blank=True)
    current_country = models.CharField(max_length=100, blank=True)
    current_state = models.CharField(max_length=100, blank=True)
    current_city = models.CharField(max_length=100, blank=True)
    monthly_remittance_ngn = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    remittance_frequency = models.CharField(max_length=20, blank=True, choices=[
        ("weekly", "Weekly"), ("monthly", "Monthly"), ("quarterly", "Quarterly"),
        ("annually", "Annually"), ("irregular", "Irregular"),
    ])
    willing_to_invest = models.BooleanField(default=False)
    willing_to_mentor = models.BooleanField(default=False)
    willing_to_return = models.BooleanField(default=False)
    willing_to_volunteer = models.BooleanField(default=False)
    observatory_person_id = models.CharField(max_length=50, blank=True, help_text="ID in abia.migrants if cross-referenced")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Beneficiary"
        verbose_name_plural = "Beneficiaries"
        ordering = ["-enrolled_date"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.current_status}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.other_names} {self.last_name}".strip()

    @property
    def age(self):
        from datetime import date
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class PillarParticipation(models.Model):
    PILLAR_CHOICES = [
        ("p1", "Pillar 1 — Migration Governance & Information"),
        ("p2", "Pillar 2 — Language & Cultural Competency"),
        ("p3", "Pillar 3 — Skills Development & Certification"),
        ("p4", "Pillar 4 — Return & Reintegration Support"),
    ]

    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name="pillar_participations")
    pillar = models.CharField(max_length=2, choices=PILLAR_CHOICES)
    enrolled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    dropped_out = models.BooleanField(default=False)
    dropout_reason = models.TextField(blank=True)
    counseling_sessions_attended = models.PositiveIntegerField(default=0)
    total_counseling_sessions = models.PositiveIntegerField(default=0)
    migration_pathway = models.CharField(max_length=50, blank=True, choices=[
        ("student_visa", "Student Visa"), ("skilled_worker", "Skilled Worker Visa"),
        ("family_reunion", "Family Reunion"), ("business_visa", "Business Visa"),
        ("tourist_visa", "Tourist Visa"), ("irregular", "Irregular Route"), ("undecided", "Undecided"),
    ])
    destination_country = models.CharField(max_length=100, blank=True)
    trafficking_vulnerability_baseline = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    trafficking_vulnerability_exit = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True)
    protection_referral_made = models.BooleanField(default=False)
    protection_referral_date = models.DateField(null=True, blank=True)
    language_course = models.CharField(max_length=50, blank=True, choices=[
        ("german", "German"), ("french", "French"), ("arabic", "Arabic"),
        ("italian", "Italian"), ("spanish", "Spanish"), ("portuguese", "Portuguese"),
        ("chinese", "Chinese"), ("other", "Other"),
    ])
    language_proficiency_baseline = models.CharField(max_length=10, blank=True)
    language_proficiency_exit = models.CharField(max_length=10, blank=True)
    cultural_orientation_modules = models.PositiveIntegerField(default=0)
    cultural_orientation_completed = models.BooleanField(default=False)
    integration_readiness_score = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    training_sector = models.CharField(max_length=100, blank=True)
    training_hours_completed = models.PositiveIntegerField(default=0)
    training_hours_total = models.PositiveIntegerField(default=0)
    certification_issued = models.BooleanField(default=False)
    certification_type = models.CharField(max_length=100, blank=True, choices=[
        ("national", "National Certificate"), ("international", "International Certificate"),
        ("industry", "Industry-Recognized"), ("vocational", "Vocational Diploma"),
    ])
    certification_body = models.CharField(max_length=200, blank=True)
    certification_date = models.DateField(null=True, blank=True)
    skills_market_alignment_score = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    placement_status = models.CharField(max_length=30, blank=True, choices=[
        ("employed_domestic", "Employed — Domestic"), ("employed_abroad", "Employed — Abroad"),
        ("self_employed", "Self-employed"), ("unemployed", "Unemployed"), ("further_study", "Further Study"),
    ])
    placement_employer = models.CharField(max_length=200, blank=True)
    placement_date = models.DateField(null=True, blank=True)
    placement_salary_ngn = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    returnee_needs_assessment = models.TextField(blank=True)
    reintegration_package_type = models.CharField(max_length=100, blank=True, choices=[
        ("cash_grant", "Cash Grant"), ("equipment", "Equipment / Tools"),
        ("training", "Skills Training"), ("psychosocial", "Psychosocial Support"),
        ("housing", "Housing Support"), ("combined", "Combined Package"),
    ])
    reintegration_package_value_ngn = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reintegration_package_delivered = models.BooleanField(default=False)
    reintegration_package_date = models.DateField(null=True, blank=True)
    business_incubation_enrolled = models.BooleanField(default=False)
    mentor_assigned = models.CharField(max_length=200, blank=True)
    micro_enterprise_registered = models.BooleanField(default=False)
    business_cac_number = models.CharField(max_length=20, blank=True)
    business_sector = models.CharField(max_length=100, blank=True)
    business_employees = models.PositiveIntegerField(default=0)
    alumni_network_member = models.BooleanField(default=False)
    alumni_engagement_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pillar Participation"
        verbose_name_plural = "Pillar Participations"
        unique_together = ["beneficiary", "pillar"]
        ordering = ["-enrolled_date"]

    def __str__(self):
        return f"{self.beneficiary.full_name} — {self.get_pillar_display()}"

    @property
    def completion_rate(self):
        if self.pillar == "p1" and self.total_counseling_sessions > 0:
            return round((self.counseling_sessions_attended / self.total_counseling_sessions) * 100, 1)
        if self.pillar == "p3" and self.training_hours_total > 0:
            return round((self.training_hours_completed / self.training_hours_total) * 100, 1)
        return None

class ProgramOutcomeSnapshot(models.Model):
    PERIOD_CHOICES = [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")]

    snapshot_date = models.DateField()
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="quarterly")
    year = models.PositiveIntegerField()
    quarter = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(4)])
    month = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)])
    p1_counseled_total = models.PositiveIntegerField(default=0)
    p1_counseled_target = models.PositiveIntegerField(default=0)
    p1_regular_pathway_uptake = models.PositiveIntegerField(default=0)
    p1_irregular_pathway_uptake = models.PositiveIntegerField(default=0)
    p1_trafficking_referrals = models.PositiveIntegerField(default=0)
    p1_info_sessions_held = models.PositiveIntegerField(default=0)
    p1_materials_distributed = models.PositiveIntegerField(default=0)
    p2_language_enrolled_total = models.PositiveIntegerField(default=0)
    p2_cultural_orientation_completed = models.PositiveIntegerField(default=0)
    p2_avg_integration_readiness = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    p3_trained_total = models.PositiveIntegerField(default=0)
    p3_trained_target = models.PositiveIntegerField(default=0)
    p3_certifications_issued = models.PositiveIntegerField(default=0)
    p3_placed_employed = models.PositiveIntegerField(default=0)
    p3_placed_self_employed = models.PositiveIntegerField(default=0)
    p3_placed_abroad = models.PositiveIntegerField(default=0)
    p3_unemployed = models.PositiveIntegerField(default=0)
    p4_returnees_supported = models.PositiveIntegerField(default=0)
    p4_returnees_target = models.PositiveIntegerField(default=0)
    p4_reintegration_packages = models.PositiveIntegerField(default=0)
    p4_micro_enterprises = models.PositiveIntegerField(default=0)
    p4_micro_enterprises_target = models.PositiveIntegerField(default=0)
    p4_businesses_surviving_6mo = models.PositiveIntegerField(default=0)
    p4_businesses_surviving_12mo = models.PositiveIntegerField(default=0)
    p4_alumni_active = models.PositiveIntegerField(default=0)
    total_budget_period = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_spent_period = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    p1_spent = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    p2_spent = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    p3_spent = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    p4_spent = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    count_abia = models.PositiveIntegerField(default=0)
    count_se_other = models.PositiveIntegerField(default=0)
    count_other_ng = models.PositiveIntegerField(default=0)
    count_abroad = models.PositiveIntegerField(default=0)
    count_male = models.PositiveIntegerField(default=0)
    count_female = models.PositiveIntegerField(default=0)
    count_other_gender = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_by = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Program Outcome Snapshot"
        verbose_name_plural = "Program Outcome Snapshots"
        unique_together = ["year", "quarter", "month", "period_type"]
        ordering = ["-snapshot_date"]

    def __str__(self):
        if self.period_type == "monthly" and self.month:
            return f"Snapshot {self.year}-M{self.month}"
        if self.period_type == "quarterly" and self.quarter:
            return f"Snapshot {self.year}-Q{self.quarter}"
        return f"Snapshot {self.year}"

    @property
    def utilization_rate(self):
        if self.total_budget_period == 0:
            return 0
        return round((self.total_spent_period / self.total_budget_period) * 100, 2)

    @property
    def cost_per_beneficiary(self):
        total = self.count_abia + self.count_se_other + self.count_other_ng + self.count_abroad
        if total == 0:
            return 0
        return round(self.total_spent_period / total, 2)

class PolicyEvidence(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    pillar_focus = models.CharField(max_length=10, blank=True, choices=[
        ("p1", "Pillar 1"), ("p2", "Pillar 2"), ("p3", "Pillar 3"), ("p4", "Pillar 4"), ("all", "All Pillars"),
    ])
    data_sources = models.TextField(help_text="Which tracker queries or reports generated this evidence")
    key_findings = models.TextField(blank=True)
    policy_brief_url = models.URLField(blank=True)
    policy_brief_file = models.FileField(upload_to="policy_briefs/", blank=True)
    submitted_to = models.CharField(max_length=300, blank=True)
    submission_date = models.DateField(null=True, blank=True)
    decision_outcome = models.TextField(blank=True)
    outcome_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Policy Evidence"
        verbose_name_plural = "Policy Evidence"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class StakeholderEngagement(models.Model):
    PARTNER_CHOICES = [
        ("iom", "International Organization for Migration (IOM)"),
        ("ncfrmi", "National Commission for Refugees, Migrants and IDPs (NCFRMI)"),
        ("csonetmade", "CSOnetMADE"),
        ("ama", "Abia Migration Agency (AMA)"),
        ("polytechnic", "Ogbonnaya Onu Polytechnic"),
        ("state_govt", "Abia State Government"),
        ("federal_govt", "Federal Government Agency"),
        ("diaspora_assoc", "Diaspora Association"),
        ("private_sector", "Private Sector Partner"),
        ("other", "Other"),
    ]
    ACTIVITY_CHOICES = [
        ("training", "Training Delivery"), ("counseling", "Counseling Support"),
        ("funding", "Funding / Grant"), ("technical", "Technical Assistance"),
        ("policy", "Policy Dialogue"), ("monitoring", "Monitoring Visit"),
        ("research", "Joint Research"), ("other", "Other"),
    ]

    partner = models.CharField(max_length=20, choices=PARTNER_CHOICES)
    partner_other = models.CharField(max_length=200, blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.TextField()
    pillar = models.CharField(max_length=2, choices=PillarParticipation.PILLAR_CHOICES, blank=True)
    beneficiaries_reached = models.PositiveIntegerField(default=0)
    value_ngn = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    engagement_date = models.DateField()
    follow_up_required = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Stakeholder Engagement"
        verbose_name_plural = "Stakeholder Engagements"
        ordering = ["-engagement_date"]

    def __str__(self):
        return f"{self.get_partner_display()} — {self.get_activity_type_display()} ({self.engagement_date})"


class ProgramSession(models.Model):
    """A scheduled training/counseling session under a PillarParticipation."""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed'),
    ]

    pillar_participation = models.ForeignKey(
        PillarParticipation, on_delete=models.CASCADE, related_name='sessions'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=200, blank=True)
    facilitator = models.CharField(max_length=200, blank=True)
    max_participants = models.PositiveIntegerField(default=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    materials_used = models.TextField(blank=True, help_text="List of training materials consumed")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-session_date', '-start_time']
        verbose_name = 'Program Session'
        verbose_name_plural = 'Program Sessions'

    def __str__(self):
        return f"{self.title} ({self.session_date})"


class Attendance(models.Model):
    """Beneficiary attendance record for a specific session."""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
        ('late', 'Late'),
    ]

    session = models.ForeignKey(ProgramSession, on_delete=models.CASCADE, related_name='attendances')
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    participation_score = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'beneficiary']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.beneficiary.full_name} — {self.session.title} ({self.status})"


class Facilitator(models.Model):
    """External or internal trainer/facilitator."""
    TYPE_CHOICES = [
        ('internal', 'Internal Staff'),
        ('external', 'External Consultant'),
        ('volunteer', 'Volunteer'),
        ('diaspora', 'Diaspora Mentor'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    facilitator_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='external')
    organization = models.CharField(max_length=200, blank=True)
    expertise_sectors = models.CharField(max_length=300, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Facilitator'
        verbose_name_plural = 'Facilitators'

    def __str__(self):
        return self.full_name


class TrainingInventory(models.Model):
    """Track equipment, materials, and supplies for training programs."""
    CATEGORY_CHOICES = [
        ('ict', 'ICT Equipment'),
        ('tool', 'Hand Tools / Machinery'),
        ('material', 'Raw Material'),
        ('stationery', 'Stationery'),
        ('ppe', 'PPE / Safety Gear'),
        ('furniture', 'Furniture'),
        ('other', 'Other'),
    ]

    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    quantity_on_hand = models.PositiveIntegerField(default=0)
    quantity_issued = models.PositiveIntegerField(default=0)
    unit_cost_ngn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, help_text="Storage location / warehouse")
    reorder_level = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'item_name']
        verbose_name = 'Training Inventory Item'
        verbose_name_plural = 'Training Inventory Items'

    def __str__(self):
        return f"{self.item_name} ({self.quantity_on_hand} in stock)"

    @property
    def total_value_ngn(self):
        return self.quantity_on_hand * self.unit_cost_ngn

    @property
    def needs_reorder(self):
        return self.quantity_on_hand <= self.reorder_level
