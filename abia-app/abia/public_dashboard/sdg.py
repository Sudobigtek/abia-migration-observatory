"""SDG and Global Compact for Migration alignment calculator."""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from django.db.models import Count
from abia.cases.models import Case
from abia.migrants.models import Migrant


class SDGCalculator:
    SDG_GOALS = {
        8: "Decent Work and Economic Growth",
        10: "Reduced Inequalities",
        16: "Peace, Justice and Strong Institutions",
        17: "Partnerships for the Goals",
    }

    GCM_OBJECTIVES = {
        1: "Collect and utilize accurate and disaggregated data",
        3: "Provide accurate information at all stages of migration",
        7: "Address and reduce vulnerabilities in migration",
        14: "Enhance consular protection and assistance",
        15: "Provide access to basic services for migrants",
        22: "Establish mechanisms for portability of social security",
        23: "Strengthen international cooperation on return and reintegration",
    }

    @staticmethod
    def calculate_all() -> Dict[str, Any]:
        return {
            "goals": SDGCalculator.SDG_GOALS,
            "gcm_objectives": SDGCalculator.GCM_OBJECTIVES,
            "sdg_8": SDGCalculator._sdg_8_work(),
            "sdg_10": SDGCalculator._sdg_10_equality(),
            "sdg_16": SDGCalculator._sdg_16_justice(),
            "sdg_17": SDGCalculator._sdg_17_partnerships(),
            "gcm_1": SDGCalculator._gcm_1_data(),
            "gcm_3": SDGCalculator._gcm_3_information(),
            "gcm_7": SDGCalculator._gcm_7_vulnerabilities(),
            "gcm_15": SDGCalculator._gcm_15_services(),
            "gcm_23": SDGCalculator._gcm_23_reintegration(),
            "last_updated": datetime.now(),
        }

    @staticmethod
    def _sdg_8_work() -> Dict[str, Any]:
        try:
            total = Migrant.objects.count()
            employed = Migrant.objects.filter(
                occupation__isnull=False
            ).exclude(occupation="").count()
            return {
                "target": "8.8 Protect labour rights and promote safe working environments",
                "metric": "Migrants with recorded occupation",
                "value": employed,
                "total": total,
                "percentage": round((employed / total * 100), 1) if total else 0,
            }
        except Exception:
            return {"target": "8.8", "metric": "Employment data", "value": 0, "total": 0, "percentage": 0}

    @staticmethod
    def _sdg_10_equality() -> Dict[str, Any]:
        try:
            cases_by_type = list(
                Case.objects.values("case_type")
                .annotate(count=Count("id"))
                .order_by("-count")
            )
            return {
                "target": "10.7 Facilitate orderly, safe, regular and responsible migration",
                "metric": "Cases by type (indicating inequality areas)",
                "breakdown": cases_by_type,
                "total_cases": sum(c["count"] for c in cases_by_type),
            }
        except Exception:
            return {"target": "10.7", "metric": "Case breakdown", "breakdown": [], "total_cases": 0}

    @staticmethod
    def _sdg_16_justice() -> Dict[str, Any]:
        try:
            resolved = Case.objects.filter(status="resolved").count()
            total = Case.objects.count()
            return {
                "target": "16.3 Promote the rule of law and ensure equal access to justice",
                "metric": "Case resolution rate",
                "resolved": resolved,
                "total": total,
                "percentage": round((resolved / total * 100), 1) if total else 0,
            }
        except Exception:
            return {"target": "16.3", "metric": "Justice access", "resolved": 0, "total": 0, "percentage": 0}

    @staticmethod
    def _sdg_17_partnerships() -> Dict[str, Any]:
        try:
            six_months = datetime.now() - timedelta(days=180)
            recent_cases = Case.objects.filter(created_at__gte=six_months).count()
            return {
                "target": "17.16 Enhance the Global Partnership for Sustainable Development",
                "metric": "Cases handled in last 6 months (partnership indicator)",
                "value": recent_cases,
                "period": "Last 180 days",
            }
        except Exception:
            return {"target": "17.16", "metric": "Partnership activity", "value": 0, "period": "Last 180 days"}

    @staticmethod
    def _gcm_1_data() -> Dict[str, Any]:
        try:
            total = Migrant.objects.count()
            with_occupation = Migrant.objects.filter(
                occupation__isnull=False
            ).exclude(occupation="").count()
            return {
                "objective": "1. Collect and utilize accurate and disaggregated data",
                "metric": "Registered migrants with complete data profiles",
                "total_registered": total,
                "complete_profiles": with_occupation,
                "percentage": round((with_occupation / total * 100), 1) if total else 0,
            }
        except Exception:
            return {"objective": "GCM 1", "metric": "Data completeness", "total_registered": 0, "complete_profiles": 0, "percentage": 0}

    @staticmethod
    def _gcm_3_information() -> Dict[str, Any]:
        try:
            total = Migrant.objects.count()
            with_contact = Migrant.objects.filter(
                phone__isnull=False
            ).exclude(phone="").count()
            return {
                "objective": "3. Provide accurate information at all stages of migration",
                "metric": "Migrants with contact information for communication",
                "total": total,
                "with_contact": with_contact,
                "percentage": round((with_contact / total * 100), 1) if total else 0,
            }
        except Exception:
            return {"objective": "GCM 3", "metric": "Contact coverage", "total": 0, "with_contact": 0, "percentage": 0}

    @staticmethod
    def _gcm_7_vulnerabilities() -> Dict[str, Any]:
        try:
            vulnerable = Case.objects.filter(
                priority__in=["high", "critical"]
            ).count()
            total = Case.objects.count()
            return {
                "objective": "7. Address and reduce vulnerabilities in migration",
                "metric": "High/critical priority cases (vulnerability indicator)",
                "vulnerable_cases": vulnerable,
                "total_cases": total,
                "percentage": round((vulnerable / total * 100), 1) if total else 0,
            }
        except Exception:
            return {"objective": "GCM 7", "metric": "Vulnerability cases", "vulnerable_cases": 0, "total_cases": 0, "percentage": 0}

    @staticmethod
    def _gcm_15_services() -> Dict[str, Any]:
        try:
            total_cases = Case.objects.count()
            resolved = Case.objects.filter(status="resolved").count()
            return {
                "objective": "15. Provide access to basic services for migrants",
                "metric": "Cases resolved (service delivery indicator)",
                "resolved": resolved,
                "total": total_cases,
                "percentage": round((resolved / total_cases * 100), 1) if total_cases else 0,
            }
        except Exception:
            return {"objective": "GCM 15", "metric": "Service access", "resolved": 0, "total": 0, "percentage": 0}

    @staticmethod
    def _gcm_23_reintegration() -> Dict[str, Any]:
        try:
            returnee_cases = Case.objects.filter(
                case_type__icontains="returnee"
            ).count()
            total = Case.objects.count()
            return {
                "objective": "23. Strengthen international cooperation on return and reintegration",
                "metric": "Returnee reintegration cases handled",
                "returnee_cases": returnee_cases,
                "total_cases": total,
                "percentage": round((returnee_cases / total * 100), 1) if total else 0,
            }
        except Exception:
            return {"objective": "GCM 23", "metric": "Reintegration cases", "returnee_cases": 0, "total_cases": 0, "percentage": 0}