from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
import hashlib

User = get_user_model()

class Sector(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    blacklisted_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['code']
    def __str__(self):
        return f"{self.code}: {self.name}"

class Occupation(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='occupations')
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    skills_required = models.TextField(blank=True)
    experience_years_min = models.PositiveIntegerField(default=0)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    blacklisted_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['code']
    def __str__(self):
        return f"{self.code}: {self.title}"

class EmbassyMission(models.Model):
    MISSION_TYPE = [
        ('embassy', 'Embassy'), ('consulate', 'Consulate'),
        ('high_commission', 'High Commission'), ('liaison', 'Liaison Office'),
    ]
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    mission_type = models.CharField(max_length=20, choices=MISSION_TYPE)
    mission_name = models.CharField(max_length=300)
    labour_attache_name = models.CharField(max_length=200, blank=True)
    labour_attache_email = models.EmailField(blank=True)
    labour_attache_phone = models.CharField(max_length=30, blank=True)
    mou_signed = models.BooleanField(default=False)
    mou_date = models.DateField(null=True, blank=True)
    bla_aligned = models.BooleanField(default=False, verbose_name="Bilateral Labour Agreement Aligned")
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    blacklisted_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['country', 'city']
        verbose_name = 'Embassy / Mission'
    def __str__(self):
        return f"{self.mission_name} ({self.city})"

class ForeignEmployer(models.Model):
    COMPLIANCE_TIER = [
        ('platinum', 'Platinum — Exemplary'), ('gold', 'Gold — Compliant'),
        ('silver', 'Silver — Monitoring'), ('bronze', 'Bronze — Review Required'),
        ('blacklisted', 'Blacklisted'),
    ]
    company_name = models.CharField(max_length=300)
    trading_name = models.CharField(max_length=300, blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    company_reg = models.CharField(max_length=100, blank=True, verbose_name="Company Registration / Tax ID")
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    compliance_tier = models.CharField(max_length=20, choices=COMPLIANCE_TIER, default='silver')
    compliance_score = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    embassy_verified = models.BooleanField(default=False)
    verified_by_mission = models.ForeignKey(EmbassyMission, on_delete=models.SET_NULL, null=True, blank=True)
    verification_date = models.DateField(null=True, blank=True)
    total_workers_sourced = models.PositiveIntegerField(default=0)
    active_workers = models.PositiveIntegerField(default=0)
    worker_complaints = models.PositiveIntegerField(default=0)
    contract_compliance_rate = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    avg_salary_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    blacklist_reason = models.TextField(blank=True)
    blacklisted_at = models.DateField(null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    blacklisted_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-compliance_score', 'company_name']
        verbose_name = 'Foreign Employer'
    def __str__(self):
        return f"{self.company_name} ({self.country})"

class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('open', 'Open'), ('screening', 'Screening'),
        ('filled', 'Filled'), ('closed', 'Closed'), ('cancelled', 'Cancelled'),
    ]
    CONTRACT_TYPE = [
        ('permanent', 'Permanent'), ('contract', 'Fixed Contract'),
        ('seasonal', 'Seasonal'), ('domestic', 'Domestic Service'),
    ]
    vacancy_code = models.CharField(max_length=30, unique=True)
    employer = models.ForeignKey(ForeignEmployer, on_delete=models.CASCADE, related_name='vacancies')
    occupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='vacancies')
    title = models.CharField(max_length=300)
    positions_available = models.PositiveIntegerField(default=1)
    positions_filled = models.PositiveIntegerField(default=0)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE)
    salary_usd = models.DecimalField(max_digits=12, decimal_places=2)
    salary_currency = models.CharField(max_length=3, default='USD')
    accommodation_included = models.BooleanField(default=False)
    accommodation_quality = models.CharField(max_length=20, blank=True, choices=[('good','Good'),('adequate','Adequate'),('poor','Poor')])
    location_city = models.CharField(max_length=100)
    location_country = models.CharField(max_length=100)
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    posted_by_mission = models.ForeignKey(EmbassyMission, on_delete=models.SET_NULL, null=True, blank=True)
    posted_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    blacklisted_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['-posted_date']
        verbose_name_plural = 'Vacancies'
    def __str__(self):
        return f"{self.vacancy_code}: {self.title}"

class TalentPool(models.Model):
    PIPELINE_STAGE = [
        ('registered', 'Registered'), ('screened', 'Screened'),
        ('matched', 'Matched to Vacancy'), ('interviewed', 'Interviewed'),
        ('endorsed', 'Endorsed'), ('deployed', 'Deployed'), ('returned', 'Returned'),
    ]
    japa_beneficiary_id = models.CharField(max_length=50, blank=True, help_text="Link to japa_development.Beneficiary")
    observatory_person_id = models.CharField(max_length=50, blank=True, help_text="Link to migrants.Migrant")
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male','Male'),('female','Female'),('other','Other')])
    lga = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    occupation = models.ForeignKey(Occupation, on_delete=models.SET_NULL, null=True, blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    skills_certifications = models.TextField(blank=True)
    preferred_destinations = models.CharField(max_length=300, blank=True)
    stage = models.CharField(max_length=20, choices=PIPELINE_STAGE, default='registered')
    assigned_vacancy = models.ForeignKey(Vacancy, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidates')
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    blacklisted_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.full_name} — {self.get_stage_display()}"

class Deployment(models.Model):
    WELFARE_STATUS = [
        ('good', 'Good — No concerns'), ('concern', 'Concern — Minor issues'),
        ('critical', 'Critical — Intervention required'), ('resolved', 'Resolved — Issue closed'),
    ]
    candidate = models.ForeignKey(TalentPool, on_delete=models.CASCADE, related_name='deployments')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='deployments')
    deployment_date = models.DateField()
    contract_start = models.DateField()
    contract_end = models.DateField(null=True, blank=True)
    salary_agreed_usd = models.DecimalField(max_digits=12, decimal_places=2)
    accommodation_provided = models.BooleanField(default=False)
    accommodation_quality = models.CharField(max_length=20, blank=True, choices=[('good','Good'),('adequate','Adequate'),('poor','Poor')])
    welfare_status = models.CharField(max_length=20, choices=WELFARE_STATUS, default='good')
    last_welfare_check = models.DateField(null=True, blank=True)
    embassy_notified = models.BooleanField(default=False)
    anonymised_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-deployment_date']
    def __str__(self):
        return f"{self.candidate.full_name} → {self.vacancy.employer.company_name}"

class CredentialEndorsement(models.Model):
    endorsement_number = models.CharField(max_length=50, unique=True)
    candidate = models.ForeignKey(TalentPool, on_delete=models.CASCADE, related_name='endorsements')
    deployment = models.ForeignKey(Deployment, on_delete=models.SET_NULL, null=True, blank=True)
    issued_by = models.CharField(max_length=200, default="Abia State Migration Agency")
    issued_date = models.DateField(auto_now_add=True)
    valid_until = models.DateField()
    destination_country = models.CharField(max_length=100)
    purpose = models.CharField(max_length=100, choices=[
        ('skilled_work','Skilled Work'),('domestic_work','Domestic Work'),
        ('healthcare','Healthcare'),('education','Education'),('business','Business')
    ])
    verification_hash = models.CharField(max_length=64, blank=True)
    qr_payload = models.CharField(max_length=300, blank=True)
    is_revoked = models.BooleanField(default=False)
    revocation_reason = models.TextField(blank=True)
    class Meta:
        ordering = ['-issued_date']
    def __str__(self):
        return self.endorsement_number
    def save(self, *args, **kwargs):
        if not self.verification_hash:
            raw = f"{self.endorsement_number}:{self.candidate_id}:{self.issued_date}:{self.destination_country}"
            self.verification_hash = hashlib.sha256(raw.encode()).hexdigest()
        super().save(*args, **kwargs)

class WelfareCheck(models.Model):
    CHECK_TYPE = [
        ('routine','Routine 30-day'),('incident','Incident-triggered'),
        ('embassy','Embassy request'),('repatriation','Repatriation assessment')
    ]
    deployment = models.ForeignKey(Deployment, on_delete=models.CASCADE, related_name='welfare_checks')
    check_date = models.DateField()
    check_type = models.CharField(max_length=20, choices=CHECK_TYPE, default='routine')
    salary_paid_on_time = models.BooleanField(default=True)
    accommodation_acceptable = models.BooleanField(default=True)
    working_hours_compliant = models.BooleanField(default=True)
    medical_access_ok = models.BooleanField(default=True)
    worker_statement = models.TextField(blank=True)
    concerns_raised = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    escalated_to_embassy = models.BooleanField(default=False)
    checked_by = models.CharField(max_length=200, blank=True)
    class Meta:
        ordering = ['-check_date']

class GrievanceTicket(models.Model):
    STATUS = [
        ('open','Open'),('investigating','Investigating'),
        ('resolved','Resolved'),('escalated','Escalated to Embassy'),('closed','Closed')
    ]
    SEVERITY = [('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')]
    deployment = models.ForeignKey(Deployment, on_delete=models.CASCADE, related_name='grievances')
    ticket_number = models.CharField(max_length=30, unique=True)
    reported_date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=100, choices=[
        ('unpaid_wages','Unpaid Wages'),('abuse','Abuse/Mistreatment'),
        ('contract_breach','Contract Breach'),('poor_accommodation','Poor Accommodation'),
        ('medical_neglect','Medical Neglect'),('other','Other')
    ])
    severity = models.CharField(max_length=20, choices=SEVERITY)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='open')
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateField(null=True, blank=True)
    class Meta:
        ordering = ['-reported_date']

class TransparencyReport(models.Model):
    PERIOD = [("monthly","Monthly"),("quarterly","Quarterly"),("annual","Annual")]
    snapshot_date = models.DateField()
    period_type = models.CharField(max_length=10, choices=PERIOD, default="quarterly")
    year = models.PositiveIntegerField()
    quarter = models.PositiveIntegerField(null=True, blank=True)
    workers_deployed_total = models.PositiveIntegerField(default=0)
    workers_by_sector = models.JSONField(default=dict)
    workers_by_destination = models.JSONField(default=dict)
    workers_by_lga = models.JSONField(default=dict)
    avg_salary_by_sector_usd = models.JSONField(default=dict)
    welfare_good_pct = models.PositiveIntegerField(default=0)
    welfare_concern_pct = models.PositiveIntegerField(default=0)
    welfare_critical_pct = models.PositiveIntegerField(default=0)
    employers_verified = models.PositiveIntegerField(default=0)
    employers_blacklisted = models.PositiveIntegerField(default=0)
    endorsements_issued = models.PositiveIntegerField(default=0)
    endorsements_revoked = models.PositiveIntegerField(default=0)
    grievances_open = models.PositiveIntegerField(default=0)
    grievances_resolved = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ['year','quarter','period_type']
        ordering = ['-snapshot_date']
