from django.db import models
from django.contrib.auth import get_user_model
from abia.accounts.models import LGA

User = get_user_model()


class VictimIntake(models.Model):
    INTAKE_STATUS = [
        ('rescued', 'Rescued'),
        ('referred', 'Referred'),
        ('shelter', 'In Shelter'),
        ('rehabilitation', 'Rehabilitation'),
        ('reintegrated', 'Reintegrated'),
    ]
    EXPLOITATION_TYPES = [
        ('sexual', 'Sexual Exploitation'),
        ('labor', 'Forced Labor'),
        ('domestic', 'Domestic Servitude'),
        ('organ', 'Organ Trafficking'),
        ('child_soldier', 'Child Soldier'),
        ('forced_marriage', 'Forced Marriage'),
        ('other', 'Other'),
    ]

    full_name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male','Male'),('female','Female'),('other','Other')])
    phone = models.CharField(max_length=20, blank=True)
    lga_of_origin = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True, related_name='victims_from')
    current_lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True, related_name='victims_in')
    trafficking_route = models.TextField(help_text="e.g. Aba → Lagos → Libya")
    exploitation_type = models.CharField(max_length=20, choices=EXPLOITATION_TYPES)
    perpetrator_description = models.TextField(blank=True)
    immediate_needs = models.JSONField(default=list, help_text="['medical','legal','shelter','psychosocial']")
    consent_data_sharing = models.BooleanField(default=False, help_text="Consent to share with NAPTIP")
    consent_family_contact = models.BooleanField(default=False)
    intake_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=INTAKE_STATUS, default='rescued')
    assigned_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    synced_to_naptip = models.BooleanField(default=False)
    naptip_reference = models.CharField(max_length=100, blank=True)

    class Meta:
        app_label = 'anti_trafficking'
        ordering = ['-intake_date']
        verbose_name = 'Victim Intake'
        verbose_name_plural = 'Victim Intakes'

    def __str__(self):
        return f"{self.full_name} ({self.status})"


class Shelter(models.Model):
    name = models.CharField(max_length=200)
    lga = models.ForeignKey(LGA, on_delete=models.CASCADE, related_name='shelters')
    address = models.TextField()
    capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)
    manager_name = models.CharField(max_length=100)
    manager_phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'anti_trafficking'
        verbose_name = 'Safe House / Shelter'

    def __str__(self):
        return f"{self.name} ({self.lga.name})"

    @property
    def available_beds(self):
        return self.capacity - self.current_occupancy


class ShelterStay(models.Model):
    victim = models.ForeignKey(VictimIntake, on_delete=models.CASCADE, related_name='shelter_stays')
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='stays')
    date_admitted = models.DateTimeField(auto_now_add=True)
    date_discharged = models.DateTimeField(null=True, blank=True)
    discharge_reason = models.CharField(max_length=50, blank=True, choices=[
        ('reunified', 'Family Reunified'),
        ('independent', 'Independent Living'),
        ('transferred', 'Transferred'),
        ('other', 'Other'),
    ])
    notes = models.TextField(blank=True)

    class Meta:
        app_label = 'anti_trafficking'
        verbose_name = 'Shelter Stay'

    def __str__(self):
        return f"{self.victim.full_name} at {self.shelter.name}"


class Perpetrator(models.Model):
    RISK_LEVELS = [
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical'),
    ]
    full_name = models.CharField(max_length=200)
    aliases = models.TextField(blank=True, help_text="Known aliases, separated by commas")
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male','Male'),('female','Female')])
    phone_numbers = models.TextField(blank=True)
    known_addresses = models.TextField(blank=True)
    lga_of_operation = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True, related_name='perpetrators')
    modus_operandi = models.TextField(help_text="Method of recruitment and exploitation")
    known_associates = models.TextField(blank=True)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        app_label = 'anti_trafficking'
        permissions = [
            ('view_perpetrator_database', 'Can view perpetrator database'),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.risk_level})"


class CourtCase(models.Model):
    CASE_STATUS = [
        ('pending', 'Pending'), ('arraigned', 'Arraigned'), ('trial', 'Trial'),
        ('adjourned', 'Adjourned'), ('convicted', 'Convicted'),
        ('acquitted', 'Acquitted'), ('dismissed', 'Dismissed'),
    ]
    case_number = models.CharField(max_length=50, unique=True)
    court_name = models.CharField(max_length=200)
    court_location = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True)
    victim = models.ForeignKey(VictimIntake, on_delete=models.CASCADE, related_name='court_cases')
    perpetrator = models.ForeignKey(Perpetrator, on_delete=models.CASCADE, related_name='court_cases')
    charges = models.TextField()
    prosecuting_officer = models.CharField(max_length=100)
    prosecution_agency = models.CharField(max_length=100, default='NAPTIP')
    defense_counsel = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=CASE_STATUS, default='pending')
    next_hearing_date = models.DateField(null=True, blank=True)
    verdict = models.TextField(blank=True)
    sentence = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'anti_trafficking'
        ordering = ['-next_hearing_date']

    def __str__(self):
        return f"{self.case_number} - {self.status}"


class Evidence(models.Model):
    EVIDENCE_TYPES = [
        ('photo', 'Photograph'), ('document', 'Document'), ('video', 'Video Recording'),
        ('audio', 'Audio Recording'), ('statement', 'Witness Statement'),
        ('medical', 'Medical Report'), ('digital', 'Digital Evidence'),
    ]
    case = models.ForeignKey(CourtCase, on_delete=models.CASCADE, related_name='evidence')
    evidence_type = models.CharField(max_length=20, choices=EVIDENCE_TYPES)
    description = models.TextField()
    file = models.FileField(upload_to='evidence/%Y/%m/', blank=True, null=True)
    ipfs_hash = models.CharField(max_length=100, blank=True, help_text="IPFS content identifier")
    ipfs_url = models.URLField(blank=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    collected_at = models.DateTimeField(auto_now_add=True)
    chain_of_custody = models.TextField(blank=True)

    class Meta:
        app_label = 'anti_trafficking'

    def __str__(self):
        return f"{self.evidence_type} - {self.case.case_number}"


class PsychosocialSession(models.Model):
    victim = models.ForeignKey(VictimIntake, on_delete=models.CASCADE, related_name='psychosocial_sessions')
    session_date = models.DateTimeField()
    counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    trauma_score = models.PositiveIntegerField(null=True, blank=True, help_text="1-10 scale")
    notes = models.TextField()
    next_session_date = models.DateField(null=True, blank=True)

    class Meta:
        app_label = 'anti_trafficking'

    def __str__(self):
        return f"Session {self.id} - {self.victim.full_name}"


class ReintegrationPlan(models.Model):
    PLAN_STATUS = [
        ('draft', 'Draft'), ('approved', 'Approved'), ('in_progress', 'In Progress'),
        ('completed', 'Completed'), ('abandoned', 'Abandoned'),
    ]
    victim = models.OneToOneField(VictimIntake, on_delete=models.CASCADE, related_name='reintegration_plan')
    status = models.CharField(max_length=20, choices=PLAN_STATUS, default='draft')
    family_reunification_status = models.CharField(max_length=50, blank=True, choices=[
        ('pending', 'Pending'), ('dna_testing', 'DNA Testing'), ('home_visit', 'Home Visit Conducted'),
        ('reunified', 'Reunified'), ('alternative_care', 'Alternative Care Arranged'),
    ])
    vocational_skill = models.CharField(max_length=100, blank=True)
    training_center = models.CharField(max_length=200, blank=True)
    training_start_date = models.DateField(null=True, blank=True)
    training_completion_date = models.DateField(null=True, blank=True)
    business_grant_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    business_status = models.CharField(max_length=50, blank=True, choices=[
        ('planning', 'Planning'), ('funded', 'Funded'), ('operational', 'Operational'), ('failed', 'Failed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'anti_trafficking'

    def __str__(self):
        return f"Reintegration - {self.victim.full_name}"


class CommunityAwarenessEvent(models.Model):
    EVENT_TYPES = [
        ('town_hall', 'Town Hall Meeting'), ('religious', 'Religious Gathering'),
        ('market', 'Market Sensitization'), ('school', 'School Program'),
        ('media', 'Media Campaign'), ('door_to_door', 'Door-to-Door'),
    ]
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    lga = models.ForeignKey(LGA, on_delete=models.CASCADE, related_name='awareness_events')
    venue = models.CharField(max_length=200)
    date = models.DateField()
    attendance_count = models.PositiveIntegerField(default=0)
    materials_distributed = models.PositiveIntegerField(default=0)
    facilitator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        app_label = 'anti_trafficking'

    def __str__(self):
        return f"{self.title} ({self.lga.name})"


class SchoolProgram(models.Model):
    school_name = models.CharField(max_length=200)
    lga = models.ForeignKey(LGA, on_delete=models.CASCADE, related_name='school_programs')
    program_date = models.DateField()
    students_reached = models.PositiveIntegerField(default=0)
    peer_educators_trained = models.PositiveIntegerField(default=0)
    topics_covered = models.JSONField(default=list, help_text="['safe_migration','trafficking_signs','reporting']")
    facilitator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        app_label = 'anti_trafficking'

    def __str__(self):
        return f"{self.school_name} - {self.program_date}"


class FakeJobAlert(models.Model):
    STATUS_CHOICES = [
        ('reported', 'Reported'), ('under_investigation', 'Under Investigation'),
        ('verified_fake', 'Verified Fake'), ('verified_legitimate', 'Verified Legitimate'),
        ('blacklisted', 'Blacklisted'),
    ]
    agency_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True)
    promised_job = models.CharField(max_length=200)
    promised_salary = models.CharField(max_length=100, blank=True)
    fees_demanded = models.CharField(max_length=100, blank=True)
    destination_country = models.CharField(max_length=100, blank=True)
    reporter_name = models.CharField(max_length=100, blank=True)
    reporter_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='reported')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'anti_trafficking'

    def __str__(self):
        return f"{self.agency_name} ({self.status})"


class MissingPerson(models.Model):
    STATUS_CHOICES = [
        ('missing', 'Missing'), ('located', 'Located'), ('intercepted', 'Intercepted at Border'),
        ('deceased', 'Deceased'), ('reunified', 'Reunified'),
    ]
    full_name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male','Male'),('female','Female'),('other','Other')])
    last_seen_location = models.CharField(max_length=200)
    last_seen_date = models.DateField()
    lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True, related_name='missing_persons')
    description = models.TextField(help_text="Physical description, clothing, distinguishing marks")
    photo = models.ImageField(upload_to='missing_persons/', blank=True, null=True)
    reporter_name = models.CharField(max_length=100)
    reporter_phone = models.CharField(max_length=20)
    reporter_relationship = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='missing')
    matched_victim = models.ForeignKey(VictimIntake, on_delete=models.SET_NULL, null=True, blank=True, related_name='missing_person_matches')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'anti_trafficking'

    def __str__(self):
        return f"{self.full_name} - {self.status}"


class FamilyReunification(models.Model):
    victim = models.ForeignKey(VictimIntake, on_delete=models.CASCADE, related_name='family_reunifications')
    family_contact_name = models.CharField(max_length=200)
    family_phone = models.CharField(max_length=20)
    family_address = models.TextField()
    family_lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True, related_name='family_reunifications')
    dna_test_required = models.BooleanField(default=False)
    dna_test_status = models.CharField(max_length=50, blank=True, choices=[
        ('pending', 'Pending'), ('sample_collected', 'Sample Collected'),
        ('in_lab', 'In Laboratory'), ('matched', 'Matched'), ('not_matched', 'Not Matched'),
    ])
    home_visit_conducted = models.BooleanField(default=False)
    home_visit_date = models.DateField(null=True, blank=True)
    home_visit_report = models.TextField(blank=True)
    reunification_date = models.DateField(null=True, blank=True)
    is_safe_placement = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)

    class Meta:
        app_label = 'anti_trafficking'

    def __str__(self):
        return f"Reunification - {self.victim.full_name}"
