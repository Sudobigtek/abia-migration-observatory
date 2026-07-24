"""Data access layer for public dashboard. All ORM queries live here."""
from typing import List, Dict, Any
from datetime import datetime
from django.db.models import Count, QuerySet
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.accounts.models import LGA
from abia.reports.models import GeneratedReport

ABIA_LGAS = [
    "Aba North", "Aba South", "Arochukwu", "Bende", "Ikwuano",
    "Isiala Ngwa North", "Isiala Ngwa South", "Isuikwuato", "Obi Ngwa",
    "Ohafia", "Osisioma Ngwa", "Ugwunagbo", "Ukwa East", "Ukwa West",
    "Umuahia North", "Umuahia South", "Umu Nneochi"
]

class MigrantRepository:
    @staticmethod
    def get_total_count() -> int:
        try:
            return Migrant.objects.count()
        except Exception:
            return 0

    @staticmethod
    def get_monthly_trend(since: datetime) -> List[Dict[str, Any]]:
        try:
            return list(
                Migrant.objects.filter(created_at__gte=since)
                .extra(select={"month": "TO_CHAR(created_at, 'YYYY-MM')"})
                .values("month")
                .annotate(count=Count("id"))
                .order_by("month")
            )
        except Exception:
            return []

class CaseRepository:
    @staticmethod
    def get_total_count() -> int:
        try:
            return Case.objects.count()
        except Exception:
            return 0

    @staticmethod
    def get_resolved_count() -> int:
        try:
            return Case.objects.filter(status="resolved").count()
        except Exception:
            return 0

    @staticmethod
    def get_active_count() -> int:
        try:
            return Case.objects.filter(status="active").count()
        except Exception:
            return 0

    @staticmethod
    def get_category_breakdown() -> List[Dict[str, Any]]:
        try:
            return list(
                Case.objects.values("case_type")
                .annotate(count=Count("id"))
                .order_by("-count")
            )
        except Exception:
            return []

    @staticmethod
    def create_from_feedback(data: Dict[str, Any]):
        try:
            return Case.objects.create(
                description=data.get("description", ""),
                case_type=data.get("case_type", "general"),
                priority=data.get("priority", "medium"),
                status=data.get("status", "open"),
            )
        except Exception:
            try:
                return Case.objects.create(
                    description=data.get("description", ""),
                    priority=data.get("priority", "medium"),
                    status=data.get("status", "open"),
                )
            except Exception:
                return None

class LGARepository:
    @staticmethod
    def get_all_lgas() -> List[Dict[str, Any]]:
        try:
            db_lgas = list(LGA.objects.all().order_by("name").values("id", "name"))
            if len(db_lgas) >= 17:
                return db_lgas
            db_names = {l["name"].strip().lower(): l for l in db_lgas}
            merged = []
            for lga_name in ABIA_LGAS:
                key = lga_name.strip().lower()
                if key in db_names:
                    merged.append(db_names[key])
                else:
                    merged.append({"id": None, "name": lga_name})
            return merged
        except Exception:
            return [{"id": None, "name": name} for name in ABIA_LGAS]

    @staticmethod
    def get_all_with_migrant_counts() -> List[Dict[str, Any]]:
        try:
            return list(LGA.objects.annotate(
                migrant_count=Count("migrants")
            ).values("name", "migrant_count").order_by("name"))
        except Exception:
            return [{"name": name, "migrant_count": 0} for name in ABIA_LGAS]

    @staticmethod
    def get_map_features() -> List[Dict[str, Any]]:
        try:
            lgas = LGA.objects.annotate(migrant_count=Count("migrants"))
            features = []
            for lga in lgas:
                if hasattr(lga, "geo_boundary") and lga.geo_boundary:
                    features.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                lga.geo_boundary.centroid.x,
                                lga.geo_boundary.centroid.y
                            ]
                        },
                        "properties": {
                            "name": lga.name,
                            "migrant_count": lga.migrant_count
                        }
                    })
            return features
        except Exception:
            return []

class GeneratedReportRepository:
    @staticmethod
    def get_recent_public(limit: int = 5) -> QuerySet:
        try:
            return GeneratedReport.objects.filter(
                status="completed"
            ).order_by("-generated_at")[:limit]
        except Exception:
            try:
                return GeneratedReport.objects.order_by("-generated_at")[:limit]
            except Exception:
                return GeneratedReport.objects.none()
