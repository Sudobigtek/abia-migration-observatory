"""Hardened feedback system with anti-abuse controls."""
import hashlib
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpRequest
from .exceptions import FeedbackSubmissionError

class FeedbackSecurityValidator:
    MAX_SUBMISSIONS_PER_IP_HOUR = 3
    MAX_SUBMISSIONS_PER_IP_DAY = 10
    MIN_FILL_TIME_SECONDS = 5
    SUSPICIOUS_KEYWORDS = [
        "kill", "murder", "attack", "bomb", "terrorist",
        "revenge", "eliminate", "destroy", "burn", "ambush",
        "trap", "lure", "fake tip", "false report", "swatting"
    ]
    AMBUSH_PATTERNS = [
        "come alone", "no backup", "send one person",
        "unmarked car", "plain clothes", "dont bring",
        "do not bring", "come quietly", "secret meeting",
        "officer alone", "single officer", "no uniform"
    ]

    @staticmethod
    def get_client_fingerprint(request: HttpRequest) -> Dict[str, str]:
        ip_raw = request.META.get("REMOTE_ADDR", "unknown")
        ip_hash = hashlib.sha256(ip_raw.encode()).hexdigest()[:16]
        ua_raw = request.META.get("HTTP_USER_AGENT", "unknown")
        ua_hash = hashlib.sha256(ua_raw.encode()).hexdigest()[:16]
        return {
            "ip_hash": ip_hash,
            "ip_prefix": ip_raw.split(".")[0] if "." in ip_raw else "unknown",
            "user_agent_hash": ua_hash,
            "referrer": request.META.get("HTTP_REFERER", "direct"),
            "accept_language": request.META.get("HTTP_ACCEPT_LANGUAGE", ""),
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def check_rate_limit(ip_address: str) -> Optional[str]:
        hour_count = cache.get("feedback_hour:" + ip_address, 0)
        day_count = cache.get("feedback_day:" + ip_address, 0)
        if hour_count >= 3:
            return "Rate limit exceeded. Max 3 submissions per hour."
        if day_count >= 10:
            return "Daily rate limit exceeded. Max 10 submissions per day."
        return None

    @staticmethod
    def record_submission(ip_address: str) -> None:
        cache.set(
            "feedback_hour:" + ip_address,
            cache.get("feedback_hour:" + ip_address, 0) + 1,
            3600
        )
        cache.set(
            "feedback_day:" + ip_address,
            cache.get("feedback_day:" + ip_address, 0) + 1,
            86400
        )

    @staticmethod
    def validate_form_timing(form_load_time: Optional[float], submit_time: float) -> Optional[str]:
        if not form_load_time:
            return "Form session expired. Please refresh."
        if submit_time - form_load_time < 5:
            return "Submission too fast. Please fill carefully."
        return None

    @staticmethod
    def check_honeypot(data: Dict[str, Any]) -> Optional[str]:
        if data.get("website", "").strip():
            return "Submission rejected."
        return None

    @staticmethod
    def analyze_content(description: str, subject: str) -> Dict[str, Any]:
        full_text = (subject + " " + description).lower()
        keyword_hits = [kw for kw in FeedbackSecurityValidator.SUSPICIOUS_KEYWORDS if kw in full_text]
        ambush_hits = [p for p in FeedbackSecurityValidator.AMBUSH_PATTERNS if p in full_text]
        caps_ratio = sum(1 for c in full_text if c.isupper()) / max(len(full_text), 1)
        excessive_punct = full_text.count("!!!") + full_text.count("???")
        risk_score = (
            len(keyword_hits) * 20
            + len(ambush_hits) * 35
            + (15 if caps_ratio > 0.5 else 0)
            + (10 if excessive_punct > 2 else 0)
        )
        risk_factors = []
        if keyword_hits:
            risk_factors.append("Suspicious keywords: " + ", ".join(keyword_hits))
        if ambush_hits:
            risk_factors.append("AMBUSH INDICATORS: " + ", ".join(ambush_hits))
        if caps_ratio > 0.5:
            risk_factors.append("Excessive capitalization")
        if excessive_punct > 2:
            risk_factors.append("Excessive punctuation")
        risk_level = "high" if risk_score >= 40 else "medium" if risk_score >= 20 else "low"
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "requires_manual_review": risk_level in ["high", "medium"],
            "ambush_detected": len(ambush_hits) > 0,
        }

class HardenedFeedbackService:
    @staticmethod
    def submit_feedback(form_data: Dict[str, Any], request: HttpRequest, session_data: Dict[str, Any]) -> Dict[str, Any]:
        ip_address = request.META.get("REMOTE_ADDR", "unknown")
        rate_error = FeedbackSecurityValidator.check_rate_limit(ip_address)
        if rate_error:
            raise FeedbackSubmissionError(rate_error)
        timing_error = FeedbackSecurityValidator.validate_form_timing(
            session_data.get("feedback_form_load_time"), time.time()
        )
        if timing_error:
            raise FeedbackSubmissionError(timing_error)
        honeypot_error = FeedbackSecurityValidator.check_honeypot(form_data)
        if honeypot_error:
            raise FeedbackSubmissionError(honeypot_error)
        content_analysis = FeedbackSecurityValidator.analyze_content(
            form_data.get("description", ""), form_data.get("subject", "")
        )
        fingerprint = FeedbackSecurityValidator.get_client_fingerprint(request)
        tracking_id = "FB-" + uuid.uuid4().hex[:8].upper()
        if content_analysis["ambush_detected"]:
            case_status = "security_review"
            case_priority = "critical"
        elif content_analysis["requires_manual_review"]:
            case_status = "pending_review"
            case_priority = "critical" if content_analysis["risk_level"] == "high" else form_data.get("urgency", "medium")
        else:
            case_status = "open"
            case_priority = form_data.get("urgency", "medium")
        from .repositories import CaseRepository
        case_data = {
            "description": form_data.get("description", ""),
            "case_type": form_data.get("feedback_type", "feedback"),
            "priority": case_priority,
            "status": case_status,
        }
        CaseRepository.create_from_feedback(case_data)
        FeedbackSecurityValidator.record_submission(ip_address)
        if form_data.get("email"):
            review_notice = ""
            if content_analysis["ambush_detected"]:
                review_notice = chr(10) + "SECURITY NOTICE: Your submission contains patterns requiring manual verification. An officer will contact you." + chr(10)
            elif content_analysis["requires_manual_review"]:
                review_notice = chr(10) + "NOTE: Flagged for security review. Processing may take longer." + chr(10)
            msg_lines = [
                "Dear " + form_data.get("name", "User") + ",",
                "",
                "Thank you for your feedback.",
                "Tracking ID: " + tracking_id,
                "Type: " + form_data["feedback_type"],
                "Subject: " + form_data["subject"],
                review_notice,
                "",
                "Abia State Migration Observatory",
            ]
            send_mail(
                subject="Feedback Received - Tracking ID: " + tracking_id,
                message=chr(10).join(msg_lines),
                from_email="noreply@abia-migration.gov.ng",
                recipient_list=[form_data["email"]],
                fail_silently=True
            )
        return {
            "tracking_id": tracking_id,
            "status": case_status,
            "risk_level": content_analysis["risk_level"],
            "requires_review": content_analysis["requires_manual_review"],
            "ambush_detected": content_analysis["ambush_detected"],
        }
