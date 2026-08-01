"""Business logic layer for public dashboard. No ORM imports."""
from typing import Dict, Any
from datetime import datetime, timedelta
from django.core.mail import send_mail
from .repositories import MigrantRepository, CaseRepository, LGARepository, GeneratedReportRepository
from .exceptions import FeedbackSubmissionError

class DashboardService:
    @staticmethod
    def get_dashboard_context() -> Dict[str, Any]:
        total_migrants = MigrantRepository.get_total_count()
        total_cases = CaseRepository.get_total_count()
        resolved_cases = CaseRepository.get_resolved_count()
        active_cases = CaseRepository.get_active_count()
        six_months_ago = datetime.now() - timedelta(days=180)
        return {'total_migrants': total_migrants, 'total_cases': total_cases, 'resolved_cases': resolved_cases, 'active_cases': active_cases, 'resolution_rate': round((resolved_cases / total_cases * 100), 1) if total_cases else 0, 'lga_data': list(LGARepository.get_all_with_migrant_counts()), 'monthly_trend': MigrantRepository.get_monthly_trend(six_months_ago), 'case_categories': CaseRepository.get_category_breakdown(), 'recent_reports': list(GeneratedReportRepository.get_recent_public()), 'last_updated': datetime.now()}

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
