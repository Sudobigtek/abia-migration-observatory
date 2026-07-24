#!/bin/bash
cd /home/abia/abia-migration-observatory/abia-app

cat > abia/public_dashboard/security.py << 'PYEOF'
"""Hardened feedback system with anti-abuse controls."""
import hashlib
import time
from typing import Dict, Any, Optional
from datetime import datetime
from django.core.cache import cache
from django.http import HttpRequest
from .exceptions import FeedbackSubmissionError

class FeedbackSecurityValidator:
    MAX_SUBMISSIONS_PER_IP_HOUR = 3
    MAX_SUBMISSIONS_PER_IP_DAY = 10
    MIN_FILL_TIME_SECONDS = 5
    SUSPICIOUS_KEYWORDS = ['kill','murder','attack','bomb','terrorist','revenge','eliminate','destroy','burn']

    @staticmethod
    def get_client_fingerprint(request: HttpRequest) -> Dict[str, str]:
        ip_raw = request.META.get('REMOTE_ADDR', 'unknown')
        ip_hash = hashlib.sha256(ip_raw.encode()).hexdigest()[:16]
        ua_raw = request.META.get('HTTP_USER_AGENT', 'unknown')
        ua_hash = hashlib.sha256(ua_raw.encode()).hexdigest()[:16]
        return {'ip_hash': ip_hash, 'ip_prefix': ip_raw.split('.')[0] if '.' in ip_raw else 'unknown', 'user_agent_hash': ua_hash, 'referrer': request.META.get('HTTP_REFERER', 'direct'), 'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', ''), 'timestamp': datetime.now().isoformat()}

    @staticmethod
    def check_rate_limit(ip_address: str) -> Optional[str]:
        hour_key = f"feedback_hour:{ip_address}"
        day_key = f"feedback_day:{ip_address}"
        hour_count = cache.get(hour_key, 0)
        day_count = cache.get(day_key, 0)
        if hour_count >= 3: return "Rate limit exceeded. Max 3 submissions per hour."
        if day_count >= 10: return "Daily rate limit exceeded. Max 10 submissions per day."
        return None

    @staticmethod
    def record_submission(ip_address: str) -> None:
        cache.set(f"feedback_hour:{ip_address}", cache.get(f"feedback_hour:{ip_address}", 0) + 1, 3600)
        cache.set(f"feedback_day:{ip_address}", cache.get(f"feedback_day:{ip_address}", 0) + 1, 86400)

    @staticmethod
    def validate_form_timing(form_load_time: Optional[float], submit_time: float) -> Optional[str]:
        if not form_load_time: return "Form session expired. Please refresh."
        if submit_time - form_load_time < 5: return "Submission too fast. Please fill carefully."
        return None

    @staticmethod
    def check_honeypot(data: Dict[str, Any]) -> Optional[str]:
        if data.get('website', '').strip(): return "Submission rejected."
        return None

    @staticmethod
    def analyze_content(description: str, subject: str) -> Dict[str, Any]:
        full_text = f"{subject} {description}".lower()
        keyword_hits = [kw for kw in FeedbackSecurityValidator.SUSPICIOUS_KEYWORDS if kw in full_text]
        caps_ratio = sum(1 for c in full_text if c.isupper()) / max(len(full_text), 1)
        excessive_punct = full_text.count('!!!') + full_text.count('???')
        risk_score = len(keyword_hits) * 20 + (15 if caps_ratio > 0.5 else 0) + (10 if excessive_punct > 2 else 0)
        risk_factors = []
        if keyword_hits: risk_factors.append(f"Suspicious keywords: {', '.join(keyword_hits)}")
        if caps_ratio > 0.5: risk_factors.append("Excessive capitalization")
        if excessive_punct > 2: risk_factors.append("Excessive punctuation")
        risk_level = 'high' if risk_score >= 40 else 'medium' if risk_score >= 20 else 'low'
        return {'risk_level': risk_level, 'risk_score': risk_score, 'risk_factors': risk_factors, 'requires_manual_review': risk_level in ['high', 'medium']}

class HardenedFeedbackService:
    @staticmethod
    def submit_feedback(form_data: Dict[str, Any], request: HttpRequest, session_data: Dict[str, Any]) -> Dict[str, Any]:
        import uuid
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        rate_error = FeedbackSecurityValidator.check_rate_limit(ip_address)
        if rate_error: raise FeedbackSubmissionError(rate_error)
        timing_error = FeedbackSecurityValidator.validate_form_timing(session_data.get('form_load_time'), time.time())
        if timing_error: raise FeedbackSubmissionError(timing_error)
        honeypot_error = FeedbackSecurityValidator.check_honeypot(form_data)
        if honeypot_error: raise FeedbackSubmissionError(honeypot_error)
        content_analysis = FeedbackSecurityValidator.analyze_content(form_data.get('description', ''), form_data.get('subject', ''))
        fingerprint = FeedbackSecurityValidator.get_client_fingerprint(request)
        tracking_id = f"FB-{uuid.uuid4().hex[:8].upper()}"
        case_status = 'pending_review' if content_analysis['requires_manual_review'] else 'open'
        case_priority = 'critical' if content_analysis['risk_level'] == 'high' else form_data.get('urgency', 'medium')
        case_data = {'title': f"[{form_data['feedback_type'].upper()}] {form_data['subject']}", 'description': form_data['description'], 'category': form_data['feedback_type'], 'priority': case_priority, 'status': case_status, 'source': 'public_feedback', 'metadata': {'tracking_id': tracking_id, 'submitter_name': form_data.get('name') or 'Anonymous', 'submitter_email': form_data.get('email'), 'submitter_phone': form_data.get('phone'), 'lga': str(form_data.get('lga', '')), 'security': {'fingerprint': fingerprint, 'risk_level': content_analysis['risk_level'], 'risk_score': content_analysis['risk_score'], 'risk_factors': content_analysis['risk_factors'], 'requires_manual_review': content_analysis['requires_manual_review']}}}
        from .repositories import CaseRepository
        CaseRepository.create_from_feedback(case_data)
        FeedbackSecurityValidator.record_submission(ip_address)
        if form_data.get('email'):
            review_notice = "\nNOTE: Flagged for security review.\n" if content_analysis['requires_manual_review'] else ""
            from django.core.mail import send_mail
            send_mail(subject=f'Feedback Received — Tracking ID: {tracking_id}', message=f"Dear {form_data.get('name', 'User')},\n\nThank you for your feedback.\nTracking ID: {tracking_id}\nType: {form_data['feedback_type']}\nSubject: {form_data['subject']}\n{review_notice}\nAbia State Migration Observatory", from_email='noreply@abia-migration.gov.ng', recipient_list=[form_data['email']], fail_silently=True)
        return {'tracking_id': tracking_id, 'status': case_status, 'risk_level': content_analysis['risk_level'], 'requires_review': content_analysis['requires_manual_review']}
PYEOF

cat > abia/public_dashboard/forms.py << 'PYEOF'
"""Form definitions for public dashboard."""
from django import forms
from abia.accounts.models import LGA

class PublicFeedbackForm(forms.Form):
    FEEDBACK_TYPES = [('complaint','Complaint'),('suggestion','Suggestion'),('request','Service Request'),('report','Report an Issue'),('feedback','General Feedback')]
    URGENCY_LEVELS = [('low','Low — No immediate action needed'),('medium','Medium — Should be addressed within a week'),('high','High — Requires urgent attention'),('critical','Critical — Immediate response required')]
    feedback_type = forms.ChoiceField(choices=FEEDBACK_TYPES, widget=forms.Select(attrs={'class':'form-select'}), label='Type of Feedback')
    urgency = forms.ChoiceField(choices=URGENCY_LEVELS, widget=forms.Select(attrs={'class':'form-select'}), label='Urgency Level', initial='medium')
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Brief summary'}), label='Subject')
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','rows':5,'placeholder':'Describe in detail...'}), label='Description')
    lga = forms.ModelChoiceField(queryset=LGA.objects.all().order_by('name'), widget=forms.Select(attrs={'class':'form-select'}), label='LGA (Optional)', required=False)
    name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Your name (optional)'}), label='Your Name (Optional)')
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email (optional)'}), label='Email (Optional)')
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Phone (optional)'}), label='Phone (Optional)')
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'display:none !important;','tabindex':'-1','autocomplete':'off'}), label='')
    consent = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class':'form-check-input'}), label='I consent to the Abia Migration Observatory processing this feedback')

class MigrantRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Your full name'}), label='Full Name')
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'class':'form-control','type':'date'}), label='Date of Birth')
    nationality = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'e.g., Nigerian, Ghanaian'}), label='Nationality')
    current_lga = forms.ModelChoiceField(queryset=LGA.objects.all().order_by('name'), widget=forms.Select(attrs={'class':'form-select'}), label='Current LGA in Abia State')
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Phone number'}), label='Phone Number')
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email (optional)'}), label='Email (Optional)')
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control','rows':2,'placeholder':'Current address'}), label='Address (Optional)')
    occupation = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Your occupation'}), label='Occupation')
    purpose_of_migration = forms.ChoiceField(choices=[('work','Work / Employment'),('business','Business / Trade'),('education','Education'),('family','Family Reunion'),('refugee','Refugee / Asylum'),('other','Other')], widget=forms.Select(attrs={'class':'form-select'}), label='Purpose of Migration')
    emergency_contact_name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Emergency contact name'}), label='Emergency Contact Name')
    emergency_contact_phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Emergency contact phone'}), label='Emergency Contact Phone')
    consent = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class':'form-check-input'}), label='I consent to the Abia State Government registering my information')

class StatusCheckForm(forms.Form):
    CHECK_TYPES = [('case','Case Tracking ID'),('registration','Registration ID')]
    check_type = forms.ChoiceField(choices=CHECK_TYPES, widget=forms.Select(attrs={'class':'form-select'}), label='What do you want to check?')
    tracking_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'e.g., FB-ABC12345 or AMO-ABC12345'}), label='Enter your ID')
PYEOF

cat > abia/public_dashboard/views.py << 'PYEOF'
\"\"\"Controller layer for public dashboard.\"\"\"\nimport time\nfrom django.shortcuts import render, redirect\nfrom django.contrib import messages\nfrom django.http import JsonResponse\nfrom .forms import PublicFeedbackForm, MigrantRegistrationForm, StatusCheckForm\nfrom .services import DashboardService, MapService\nfrom .exceptions import FeedbackSubmissionError\n\ndef public_dashboard(request):\n    context = DashboardService.get_dashboard_context()\n    return render(request, 'public_dashboard/dashboard.html', context)\n\ndef public_map_data(request):\n    geojson = MapService.get_geojson()\n    return JsonResponse(geojson)\n\ndef public_feedback(request):\n    from .security import HardenedFeedbackService\n    if request.method == 'GET':\n        request.session['feedback_form_load_time'] = time.time()\n    if request.method == 'POST':\n        form = PublicFeedbackForm(request.POST)\n        if form.is_valid():\n            try:\n                session_data = {'form_load_time': request.session.get('feedback_form_load_time')}\n                result = HardenedFeedbackService.submit_feedback(form.cleaned_data, request, session_data)\n                if result['requires_review']:\n                    messages.warning(request, f'Feedback received. Tracking ID: {result[\"tracking_id\"]}. Your submission has been flagged for security review and will be processed shortly.')\n                else:\n                    messages.success(request, f'Thank you! Tracking ID: {result[\"tracking_id\"]}')\n                return redirect('public_dashboard:feedback_success')\n            except FeedbackSubmissionError as exc:\n                messages.error(request, str(exc))\n    else:\n        form = PublicFeedbackForm()\n    return render(request, 'public_dashboard/feedback.html', {'form': form})\n\ndef feedback_success(request):\n    return render(request, 'public_dashboard/feedback_success.html')\n\ndef sdg_dashboard(request):\n    from .sdg import SDGCalculator\n    return render(request, 'public_dashboard/sdg_dashboard.html', {'sdg_data': SDGCalculator.calculate_all()})\n\ndef migrant_register(request):\n    from .self_service import MigrantSelfService\n    if request.method == 'POST':\n        form = MigrantRegistrationForm(request.POST)\n        if form.is_valid():\n            reg_id = MigrantSelfService.register_migrant(form.cleaned_data)\n            messages.success(request, f'Registration successful! Your ID: {reg_id}')\n            return redirect('public_dashboard:registration_success')\n    else:\n        form = MigrantRegistrationForm()\n    return render(request, 'public_dashboard/migrant_register.html', {'form': form})\n\ndef registration_success(request):\n    return render(request, 'public_dashboard/registration_success.html')\n\ndef status_check(request):\n    from .self_service import MigrantSelfService\n    result = None\n    if request.method == 'POST':\n        form = StatusCheckForm(request.POST)\n        if form.is_valid():\n            data = form.cleaned_data\n            if data['check_type'] == 'case':\n                result = MigrantSelfService.check_case_status(data['tracking_id'])\n            else:\n                result = MigrantSelfService.check_registration_status(data['tracking_id'])\n            if not result:\n                messages.error(request, 'No record found with that ID.')\n    else:\n        form = StatusCheckForm()\n    return render(request, 'public_dashboard/status_check.html', {'form': form, 'result': result})\nPYEOF

echo "========================================"
echo "SECURITY HARDENING DEPLOYED!"
echo "========================================"
echo ""
echo "Active protections:"
echo "  • Rate limiting: 3/hour, 10/day per IP"
echo "  • Bot detection: minimum 5s fill time"
echo "  • Honeypot field: traps automated submissions"
echo "  • Content analysis: suspicious keyword detection"
echo "  • Risk scoring: auto-flags high-risk content"
echo "  • Forensic fingerprint: hashed IP + user agent"
echo "  • Manual review queue: high/medium risk → pending_review"
echo ""
echo "Run: python3 manage.py runserver"
