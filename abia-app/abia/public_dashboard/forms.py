"""Form definitions for public dashboard."""
from django import forms

ABIA_LGA_CHOICES = [("", "---------")] + [
    (name, name) for name in [
        "Aba North", "Aba South", "Arochukwu", "Bende", "Ikwuano",
        "Isiala Ngwa North", "Isiala Ngwa South", "Isuikwuato", "Obi Ngwa",
        "Ohafia", "Osisioma Ngwa", "Ugwunagbo", "Ukwa East", "Ukwa West",
        "Umuahia North", "Umuahia South", "Umu Nneochi"
    ]
]


class PublicFeedbackForm(forms.Form):
    FEEDBACK_TYPES = [
        ("complaint", "Complaint"),
        ("suggestion", "Suggestion"),
        ("request", "Service Request"),
        ("report", "Report an Issue"),
        ("feedback", "General Feedback"),
    ]
    URGENCY_LEVELS = [
        ("low", "Low - No immediate action needed"),
        ("medium", "Medium - Should be addressed within a week"),
        ("high", "High - Requires urgent attention"),
        ("critical", "Critical - Immediate response required"),
    ]
    feedback_type = forms.ChoiceField(
        choices=FEEDBACK_TYPES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Type of Feedback",
    )
    urgency = forms.ChoiceField(
        choices=URGENCY_LEVELS,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Urgency Level",
        initial="medium",
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Brief summary"}),
        label="Subject",
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Describe in detail..."}),
        label="Description",
    )
    lga = forms.ChoiceField(
        choices=ABIA_LGA_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="LGA (Optional)",
        required=False,
    )
    lga_other = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Type LGA if not in list above"
        }),
        label="Other LGA (if not listed)",
    )
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name (optional)"}),
        label="Your Name (Optional)",
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email (optional)"}),
        label="Email (Optional)",
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone (optional)"}),
        label="Phone (Optional)",
    )
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"style": "display:none !important;", "tabindex": "-1", "autocomplete": "off"}),
        label="",
    )
    consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="I consent to the Abia Migration Observatory processing this feedback",
    )


class MigrantRegistrationForm(forms.Form):
    GENDER_CHOICES = [
        ("", "---------"),
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other / Prefer not to say"),
    ]
    MARITAL_CHOICES = [
        ("", "---------"),
        ("single", "Single"),
        ("married", "Married"),
        ("widowed", "Widowed"),
        ("divorced", "Divorced"),
        ("separated", "Separated"),
    ]
    EDUCATION_CHOICES = [
        ("", "---------"),
        ("none", "No Formal Education"),
        ("informal", "Informal Education"),
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("tertiary", "Tertiary"),
    ]
    PURPOSE_CHOICES = [
        ("work", "Work / Employment"),
        ("business", "Business / Trade"),
        ("education", "Education"),
        ("family", "Family Reunion"),
        ("refugee", "Refugee / Asylum"),
        ("other", "Other"),
    ]
    NEEDS_CATEGORIES = [
        ("socioeconomic", "Socioeconomic"),
        ("medical", "Medical / Health"),
        ("education", "Education"),
        ("family_reunification", "Family Reunification"),
        ("insecurity", "Insecurity / Protection"),
    ]
    SUPPORT_TYPES = [
        ("business_support", "Business Support"),
        ("vocational_training", "Vocational Training"),
        ("job_placement", "Job Placement"),
        ("education", "Education Support"),
    ]

    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Your full name"}),
        label="Full Name",
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Date of Birth",
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Gender",
        required=False,
    )
    marital_status = forms.ChoiceField(
        choices=MARITAL_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Marital Status",
        required=False,
    )
    has_children = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Do you have children?",
    )
    number_of_children = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "0"}),
        label="Number of Children",
    )
    education_level = forms.ChoiceField(
        choices=EDUCATION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Education Level",
        required=False,
    )
    nationality = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Nigerian, Ghanaian"}),
        label="Nationality",
    )
    state_of_origin = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "State of origin"}),
        label="State of Origin",
    )
    current_state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Current state of residence"}),
        label="Current State",
    )
    current_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Current city / town"}),
        label="Current City / Town",
    )
    current_lga = forms.ChoiceField(
        choices=ABIA_LGA_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Current LGA in Abia State",
    )
    current_lga_other = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Type your LGA if not in the dropdown"
        }),
        label="Other LGA (if not listed)",
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
        label="Phone Number",
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email (optional)"}),
        label="Email (Optional)",
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Current address"}),
        label="Address (Optional)",
    )
    occupation = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Your occupation"}),
        label="Occupation",
    )
    purpose_of_migration = forms.ChoiceField(
        choices=PURPOSE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Purpose of Migration",
    )
    needs_category = forms.MultipleChoiceField(
        choices=NEEDS_CATEGORIES,
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label="Needs Category (select all that apply)",
    )
    health_condition = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Any health condition? (optional)"}),
        label="Health Condition (Optional)",
    )
    support_needed = forms.MultipleChoiceField(
        choices=SUPPORT_TYPES,
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label="Support Needed (select all that apply)",
    )
    emergency_contact_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Emergency contact name"}),
        label="Emergency Contact Name",
    )
    emergency_contact_relationship = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Wife, Brother, Friend"}),
        label="Relationship to Emergency Contact",
    )
    emergency_contact_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Emergency contact phone"}),
        label="Emergency Contact Phone",
    )
    consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="I consent to the Abia State Government registering my information",
    )


class StatusCheckForm(forms.Form):
    CHECK_TYPES = [
        ("case", "Case Tracking ID"),
        ("registration", "Registration ID"),
    ]
    check_type = forms.ChoiceField(
        choices=CHECK_TYPES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="What do you want to check?",
    )
    tracking_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., FB-ABC12345 or AMO-ABC12345"}),
        label="Enter your ID",
    )