#!/bin/bash
set -e
echo "========================================"
echo "Deploying Public Dashboard Module"
echo "========================================"
cd /home/abia/abia-migration-observatory/abia-app

mkdir -p abia/public_dashboard/tests templates/public_dashboard
touch abia/public_dashboard/__init__.py abia/public_dashboard/tests/__init__.py

cat > abia/public_dashboard/exceptions.py << 'PYEOF'
"""Custom domain exceptions for public dashboard."""
class PublicDashboardError(Exception):
    """Base exception for public dashboard domain."""
    pass
class FeedbackSubmissionError(PublicDashboardError):
    """Raised when feedback submission fails."""
    pass
class MapDataError(PublicDashboardError):
    """Raised when map data cannot be retrieved."""
    pass
PYEOF

cat > abia/public_dashboard/repositories.py << 'PYEOF'
"""Data access layer for public dashboard. All ORM queries live here."""
from typing import List, Dict, Any
from datetime import datetime
from django.db.models import Count, QuerySet
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.geo.models import LGA
from abia.reports.models import Report

class MigrantRepository:
    @staticmethod
    def get_total_count() -> int:
        return Migrant.objects.count()
    @staticmethod
    def get_monthly_trend(since: datetime) -> List[Dict[str, Any]]:
        return list(Migrant.objects.filter(created_at__gte=since).extra(select={'month': "TO_CHAR(created_at, 'YYYY-MM')"}).values('month').annotate(count=Count('id')).order_by('month'))

class CaseRepository:
    @staticmethod
    def get_total_count() -> int:
        return Case.objects.count()
    @staticmethod
    def get_resolved_count() -> int:
        return Case.objects.filter(status='resolved').count()
    @staticmethod
    def get_active_count() -> int:
        return Case.objects.filter(status='active').count()
    @staticmethod
    def get_category_breakdown() -> List[Dict[str, Any]]:
        return list(Case.objects.values('category').annotate(count=Count('id')).order_by('-count'))
    @staticmethod
    def create_from_feedback(data: Dict[str, Any]) -> Case:
        return Case.objects.create(title=data['title'], description=data['description'], category=data['category'], priority=data['priority'], status='open', source='public_feedback', metadata=data.get('metadata', {}))

class LGARepository:
    @staticmethod
    def get_all_with_migrant_counts() -> QuerySet:
        return LGA.objects.annotate(migrant_count=Count('migrant')).values('name', 'migrant_count', 'geom')
    @staticmethod
    def get_map_features() -> List[Dict[str, Any]]:
        lgas = LGA.objects.annotate(migrant_count=Count('migrant'))
        features = []
        for lga in lgas:
            if lga.geom:
                features.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [lga.geom.centroid.x, lga.geom.centroid.y]}, 'properties': {'name': lga.name, 'migrant_count': lga.migrant_count}})
        return features

class ReportRepository:
    @staticmethod
    def get_recent_public(limit: int = 5) -> QuerySet:
        return Report.objects.filter(is_public=True).order_by('-created_at')[:limit]
PYEOF

cat > abia/public_dashboard/services.py << 'PYEOF'
"""Business logic layer for public dashboard. No ORM imports."""
from typing import Dict, Any
from datetime import datetime, timedelta
from django.core.mail import send_mail
from .repositories import MigrantRepository, CaseRepository, LGARepository, ReportRepository
from .exceptions import FeedbackSubmissionError

class DashboardService:
    @staticmethod
    def get_dashboard_context() -> Dict[str, Any]:
        total_migrants = MigrantRepository.get_total_count()
        total_cases = CaseRepository.get_total_count()
        resolved_cases = CaseRepository.get_resolved_count()
        active_cases = CaseRepository.get_active_count()
        six_months_ago = datetime.now() - timedelta(days=180)
        return {'total_migrants': total_migrants, 'total_cases': total_cases, 'resolved_cases': resolved_cases, 'active_cases': active_cases, 'resolution_rate': round((resolved_cases / total_cases * 100), 1) if total_cases else 0, 'lga_data': list(LGARepository.get_all_with_migrant_counts()), 'monthly_trend': MigrantRepository.get_monthly_trend(six_months_ago), 'case_categories': CaseRepository.get_category_breakdown(), 'recent_reports': list(ReportRepository.get_recent_public()), 'last_updated': datetime.now()}

class MapService:
    @staticmethod
    def get_geojson() -> Dict[str, Any]:
        return {'type': 'FeatureCollection', 'features': LGARepository.get_map_features()}

class FeedbackService:
    @staticmethod
    def submit_feedback(form_data: Dict[str, Any]) -> str:
        import uuid
        tracking_id = f"FB-{uuid.uuid4().hex[:8].upper()}"
        case_data = {'title': f"[{form_data['feedback_type'].upper()}] {form_data['subject']}", 'description': form_data['description'], 'category': form_data['feedback_type'], 'priority': form_data['urgency'], 'metadata': {'tracking_id': tracking_id, 'submitter_name': form_data.get('name') or 'Anonymous', 'submitter_email': form_data.get('email'), 'submitter_phone': form_data.get('phone'), 'lga': form_data.get('lga')}}
        try:
            CaseRepository.create_from_feedback(case_data)
        except Exception as exc:
            raise FeedbackSubmissionError(f"Failed to create case: {exc}") from exc
        FeedbackService._send_confirmation(form_data, tracking_id)
        return tracking_id
    @staticmethod
    def _send_confirmation(form_data: Dict[str, Any], tracking_id: str) -> None:
        email = form_data.get('email')
        if not email:
            return
        send_mail(subject=f'Feedback Received — Tracking ID: {tracking_id}', message=f"Dear {form_data.get('name', 'User')},\n\nThank you for your feedback.\nTracking ID: {tracking_id}\nType: {form_data['feedback_type']}\nSubject: {form_data['subject']}\n\nAbia State Migration Observatory", from_email='noreply@abia-migration.gov.ng', recipient_list=[email], fail_silently=True)
PYEOF

cat > abia/public_dashboard/forms.py << 'PYEOF'
"""Form definitions for public dashboard."""
from django import forms

class PublicFeedbackForm(forms.Form):
    FEEDBACK_TYPES = [('complaint', 'Complaint'), ('suggestion', 'Suggestion'), ('request', 'Service Request'), ('report', 'Report an Issue'), ('feedback', 'General Feedback')]
    URGENCY_LEVELS = [('low', 'Low — No immediate action needed'), ('medium', 'Medium — Should be addressed within a week'), ('high', 'High — Requires urgent attention'), ('critical', 'Critical — Immediate response required')]
    feedback_type = forms.ChoiceField(choices=FEEDBACK_TYPES, widget=forms.Select(attrs={'class': 'form-select'}), label='Type of Feedback')
    urgency = forms.ChoiceField(choices=URGENCY_LEVELS, widget=forms.Select(attrs={'class': 'form-select'}), label='Urgency Level', initial='medium')
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of your feedback'}), label='Subject')
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Please describe your feedback in detail...'}), label='Description')
    lga = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Local Government Area (optional)'}), label='LGA (Optional)')
    name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name (optional)'}), label='Your Name (Optional)')
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email for follow-up (optional)'}), label='Email (Optional)')
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (optional)'}), label='Phone (Optional)')
    consent = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), label='I consent to the Abia Migration Observatory processing this feedback')
PYEOF

cat > abia/public_dashboard/views.py << 'PYEOF'
"""Controller layer for public dashboard. Thin views: validate -> call service -> return response."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import PublicFeedbackForm
from .services import DashboardService, MapService, FeedbackService
from .exceptions import FeedbackSubmissionError

def public_dashboard(request):
    """Render public-facing migration dashboard. No auth required."""
n    context = DashboardService.get_dashboard_context()
    return render(request, 'public_dashboard/dashboard.html', context)

def public_map_data(request):
    """Return GeoJSON data for public map."""
    geojson = MapService.get_geojson()
    return JsonResponse(geojson)

def public_feedback(request):
    """Handle public feedback form submission."""
    if request.method == 'POST':
        form = PublicFeedbackForm(request.POST)
        if form.is_valid():
            try:
                tracking_id = FeedbackService.submit_feedback(form.cleaned_data)
                messages.success(request, f'Thank you! Tracking ID: {tracking_id}')
                return redirect('public_dashboard:feedback_success')
            except FeedbackSubmissionError as exc:
                messages.error(request, str(exc))
    else:
        form = PublicFeedbackForm()
    return render(request, 'public_dashboard/feedback.html', {'form': form})

def feedback_success(request):
    """Render feedback submission success page."""
    return render(request, 'public_dashboard/feedback_success.html')
PYEOF

cat > abia/public_dashboard/urls.py << 'PYEOF'
"""URL routing for public dashboard app."""
from django.urls import path
from . import views
app_name = 'public_dashboard'
urlpatterns = [
    path('', views.public_dashboard, name='dashboard'),
    path('map-data/', views.public_map_data, name='map_data'),
    path('feedback/', views.public_feedback, name='feedback'),
    path('feedback/success/', views.feedback_success, name='feedback_success'),
]
PYEOF

cat > templates/public_dashboard/dashboard.html << 'HTMLEOF'
{% extends "base.html" %}{% load static %}{% load humanize %}
{% block title %}Public Migration Dashboard | Abia State{% endblock %}
{% block extra_head %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>.public-hero{background:linear-gradient(135deg,#1e3a5f,#2d5a87);color:white;padding:3rem 2rem;border-radius:12px;margin-bottom:2rem}.public-hero h1{margin:0;font-size:2rem}.stat-card{background:white;border-radius:12px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);text-align:center;transition:transform .2s}.stat-card:hover{transform:translateY(-4px)}.stat-card .number{font-size:2.5rem;font-weight:700;color:#1e3a5f}.stat-card .label{color:#666;font-size:.9rem;margin-top:.5rem}#migration-map{height:400px;border-radius:12px}.chart-container{background:white;border-radius:12px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.08)}.last-updated{text-align:center;color:#888;font-size:.85rem;margin-top:2rem}.badge-gcm{display:inline-block;background:#e8f4f8;color:#1e3a5f;padding:.25rem .75rem;border-radius:20px;font-size:.75rem;font-weight:600;margin-right:.5rem}.feedback-btn{position:fixed;bottom:2rem;right:2rem;z-index:1000;border-radius:50px;padding:.75rem 1.5rem;box-shadow:0 4px 12px rgba(0,0,0,0.15)}</style>
{% endblock %}
{% block content %}
<div class="container-fluid">
<div class="public-hero"><h1>Abia State Migration Observatory</h1><p>Transparent, data-driven migration governance for Abia State, Nigeria</p><div class="mt-3"><span class="badge-gcm">GCM Aligned</span><span class="badge-gcm">SDG 10.7</span><span class="badge-gcm">Open Data</span></div></div>
<div class="row mb-4"><div class="col-md-3 mb-3"><div class="stat-card"><div class="number">{{ total_migrants|intcomma }}</div><div class="label">Total Migrants Registered</div></div></div><div class="col-md-3 mb-3"><div class="stat-card"><div class="number">{{ total_cases|intcomma }}</div><div class="label">Cases Managed</div></div></div><div class="col-md-3 mb-3"><div class="stat-card"><div class="number">{{ resolution_rate }}%</div><div class="label">Case Resolution Rate</div></div></div><div class="col-md-3 mb-3"><div class="stat-card"><div class="number">{{ active_cases|intcomma }}</div><div class="label">Active Cases</div></div></div></div>
<div class="row mb-4"><div class="col-lg-7 mb-3"><div class="chart-container"><h5>&#128205; Migration Distribution by LGA</h5><div id="migration-map"></div></div></div><div class="col-lg-5 mb-3"><div class="chart-container"><h5>&#128202; Monthly Registration Trend</h5><canvas id="trendChart"></canvas></div></div></div>
<div class="row mb-4"><div class="col-lg-6 mb-3"><div class="chart-container"><h5>&#128203; Case Categories</h5><canvas id="categoryChart"></canvas></div></div><div class="col-lg-6 mb-3"><div class="chart-container"><h5>&#128240; Recent Public Reports</h5>{% if recent_reports %}<div class="list-group list-group-flush">{% for report in recent_reports %}<div class="list-group-item"><strong>{{ report.title }}</strong><br><small class="text-muted">{{ report.created_at|date:"M Y" }}</small></div>{% endfor %}</div>{% else %}<p class="text-muted">No public reports available yet.</p>{% endif %}<div class="mt-3 text-center"><a href="{% url 'public_dashboard:feedback' %}" class="btn btn-primary">&#128172; Share Feedback</a></div></div></div></div>
<div class="row mb-4"><div class="col-12"><div class="chart-container text-center"><h6 class="text-muted mb-3">In Partnership With</h6><div class="d-flex justify-content-center gap-3 flex-wrap"><span class="badge bg-secondary">NCFRMI</span><span class="badge bg-secondary">IOM Nigeria</span><span class="badge bg-secondary">GIZ</span><span class="badge bg-secondary">World Bank</span><span class="badge bg-secondary">ECOWAS</span><span class="badge bg-secondary">Federal Republic of Nigeria</span></div><p class="text-muted mt-3" style="font-size:.8rem">This dashboard aligns with the Global Compact for Safe, Orderly and Regular Migration (GCM) and the UN Sustainable Development Goals (SDGs).</p></div></div></div>
<div class="last-updated">Last updated: {{ last_updated|date:"F j, Y, P" }} | Data refreshes every 6 hours</div>
</div>
<a href="{% url 'public_dashboard:feedback' %}" class="btn btn-primary feedback-btn">&#128172; Share Feedback</a>
{% endblock %}
{% block extra_js %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>const map=L.map('migration-map').setView([5.45,7.5],10);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap contributors'}).addTo(map);fetch('/public/map-data/').then(r=>r.json()).then(data=>{data.features.forEach(f=>{const c=f.geometry.coordinates,p=f.properties,count=p.migrant_count,radius=Math.max(8,Math.sqrt(count)*2),color=count>100?'#dc3545':count>50?'#fd7e14':'#28a745';L.circleMarker([c[1],c[0]],{radius:radius,fillColor:color,color:'#fff',weight:2,opacity:1,fillOpacity:.7}).addTo(map).bindPopup('<b>'+p.name+'</b><br>'+count+' migrants registered')})});new Chart(document.getElementById('trendChart'),{type:'line',data:{labels:[{% for t in monthly_trend %}'{{ t.month }}'{% if not forloop.last %},{% endif %}{% endfor %}],datasets:[{label:'New Registrations',data:[{% for t in monthly_trend %}{{ t.count }}{% if not forloop.last %},{% endif %}{% endfor %}],borderColor:'#1e3a5f',backgroundColor:'rgba(30,58,95,0.1)',fill:true,tension:.4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true}}}});new Chart(document.getElementById('categoryChart'),{type:'doughnut',data:{labels:[{% for c in case_categories %}'{{ c.category|title }}'{% if not forloop.last %},{% endif %}{% endfor %}],datasets:[{data:[{% for c in case_categories %}{{ c.count }}{% if not forloop.last %},{% endif %}{% endfor %}],backgroundColor:['#1e3a5f','#2d5a87','#4a90c2','#87ceeb','#b0d4f1']}]},options:{responsive:true,plugins:{legend:{position:'right'}}}});</script>
{% endblock %}
HTMLEOF

cat > templates/public_dashboard/feedback.html << 'HTMLEOF'
{% extends "base.html" %}{% load static %}
{% block title %}Submit Feedback | Abia Migration Observatory{% endblock %}
{% block extra_head %}<style>.feedback-hero{background:linear-gradient(135deg,#1e3a5f,#2d5a87);color:white;padding:2.5rem 2rem;border-radius:12px;margin-bottom:2rem}.feedback-card{background:white;border-radius:12px;padding:2rem;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:800px;margin:0 auto}.anonymous-note{background:#e8f4f8;border-left:4px solid #1e3a5f;padding:1rem;border-radius:0 8px 8px 0;margin-bottom:1.5rem}</style>{% endblock %}
{% block content %}
<div class="container"><div class="feedback-hero text-center"><h1>&#128172; Share Your Feedback</h1><p class="mb-0">Help us improve migration governance in Abia State</p></div><div class="feedback-card"><div class="anonymous-note"><strong>&#128274; Your privacy matters.</strong> You can submit feedback anonymously. Providing contact details helps us follow up, but it is completely optional.</div>{% if messages %}{% for message in messages %}<div class="alert alert-{{ message.tags }} alert-dismissible fade show">{{ message }}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>{% endfor %}{% endif %}<form method="post" novalidate>{% csrf_token %}<div class="row"><div class="col-md-6 mb-3">{{ form.feedback_type.label_tag }}{{ form.feedback_type }}</div><div class="col-md-6 mb-3">{{ form.urgency.label_tag }}{{ form.urgency }}</div></div><div class="mb-3">{{ form.subject.label_tag }}{{ form.subject }}</div><div class="mb-3">{{ form.description.label_tag }}{{ form.description }}</div><div class="mb-3">{{ form.lga.label_tag }}{{ form.lga }}</div><hr><p class="text-muted small">The following fields are optional:</p><div class="row"><div class="col-md-4 mb-3">{{ form.name.label_tag }}{{ form.name }}</div><div class="col-md-4 mb-3">{{ form.email.label_tag }}{{ form.email }}</div><div class="col-md-4 mb-3">{{ form.phone.label_tag }}{{ form.phone }}</div></div><div class="mb-4"><div class="form-check">{{ form.consent }}{{ form.consent.label_tag }}</div></div><div class="d-grid"><button type="submit" class="btn btn-primary btn-lg">&#128228; Submit Feedback</button></div></form></div><div class="text-center mt-4 mb-5"><a href="{% url 'public_dashboard:dashboard' %}" class="text-decoration-none">&larr; Back to Public Dashboard</a></div></div>
{% endblock %}
HTMLEOF

cat > templates/public_dashboard/feedback_success.html << 'HTMLEOF'
{% extends "base.html" %}
{% block title %}Feedback Submitted | Abia Migration Observatory{% endblock %}
{% block content %}
<div class="container text-center py-5"><div class="row justify-content-center"><div class="col-md-6"><div class="card border-0 shadow-sm"><div class="card-body p-5"><div class="mb-4"><span style="font-size:4rem;">&#9989;</span></div><h2 class="card-title mb-3">Thank You!</h2><p class="card-text text-muted">Your feedback has been successfully submitted. If you provided an email, you will receive a confirmation with your tracking ID.</p><div class="mt-4"><a href="{% url 'public_dashboard:dashboard' %}" class="btn btn-primary">Return to Dashboard</a><a href="{% url 'public_dashboard:feedback' %}" class="btn btn-outline-primary ms-2">Submit Another</a></div></div></div></div></div></div>
{% endblock %}
HTMLEOF

# Wire URLs
if ! grep -q "public_dashboard" abia/urls.py; then
    cp abia/urls.py abia/urls.py.backup.$(date +%s)
    sed -i "/urlpatterns = \\[/a\\\\    path('public/', include('abia.public_dashboard.urls'))," abia/urls.py
    echo "  ✅ Added URL pattern"
else
    echo "  ⚠️  URL already wired"
fi

# Add to INSTALLED_APPS
python3 << 'PYEOF'
import sys
settings_path = "/home/abia/abia-migration-observatory/abia-app/abia/settings.py"
with open(settings_path, 'r') as f:
    content = f.read()
if "'abia.public_dashboard'" in content:
    print("  ✅ Already in INSTALLED_APPS")
    sys.exit(0)
lines = content.split('\n')
new_lines = []
inserted = False
for i, line in enumerate(lines):
    new_lines.append(line)
    if not inserted and line.strip().startswith("'abia.") and i < len(lines) - 1:
        if not lines[i+1].strip().startswith("'abia."):
            new_lines.append("    'abia.public_dashboard',")
            inserted = True
if not inserted:
    for i, line in enumerate(new_lines):
        if line.strip() == ']' and 'INSTALLED_APPS' in ''.join(new_lines[max(0,i-10):i]):
            new_lines.insert(i, "    'abia.public_dashboard',")
            break
with open(settings_path, 'w') as f:
    f.write('\n'.join(new_lines))
print("  ✅ Added to INSTALLED_APPS")
PYEOF

echo ""
echo "========================================"
echo "DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "Run: python manage.py runserver"
echo "Visit: http://localhost:8000/public/"
echo "       http://localhost:8000/public/feedback/"
