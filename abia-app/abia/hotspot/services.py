from datetime import datetime, timedelta
from django.contrib.gis.geos import Point
from .models import HotspotPrediction

class HotspotService:
    @staticmethod
    def analyze_hotspots(period_days=90):
        from abia.migrants.models import Migrant
        from accounts.models import LGA
        from abia.cases.models import Case
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_days)
        HotspotPrediction.objects.filter(analysis_period_end=end_date).delete()
        predictions = []
        for lga in LGA.objects.all():
            migrant_count = Migrant.objects.filter(
                current_lga=lga,
                created_at__date__range=[start_date, end_date]
            ).count()
            case_count = Case.objects.filter(
                current_lga=lga,
                created_at__date__range=[start_date, end_date]
            ).count()
            risk_factors = {
                "migrant_count": migrant_count,
                "case_count": case_count,
                "case_to_migrant_ratio": round(case_count / max(migrant_count, 1), 3)
            }
            base_score = min(migrant_count / 100.0, 1.0) * 0.4
            case_score = min(case_count / 20.0, 1.0) * 0.4
            ratio_score = min(risk_factors["case_to_migrant_ratio"] * 2, 1.0) * 0.2
            risk_score = base_score + case_score + ratio_score
            if risk_score >= 0.75:
                risk_level = "critical"
            elif risk_score >= 0.5:
                risk_level = "high"
            elif risk_score >= 0.25:
                risk_level = "medium"
            else:
                risk_level = "low"
            centroid = None
            if lga.boundary:
                centroid = lga.boundary.centroid
            pred = HotspotPrediction.objects.create(
                lga=lga,
                risk_level=risk_level,
                risk_score=round(risk_score, 3),
                predicted_migrant_count=int(migrant_count * 1.1),
                contributing_factors=risk_factors,
                centroid=centroid,
                analysis_period_start=start_date,
                analysis_period_end=end_date
            )
            predictions.append(pred)
        return predictions

    @staticmethod
    def get_geojson_hotspots():
        predictions = HotspotPrediction.objects.select_related("lga").order_by("-risk_score")[:50]
        features = []
        for p in predictions:
            if p.centroid:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [p.centroid.x, p.centroid.y]
                    },
                    "properties": {
                        "lga": str(p.lga),
                        "risk_level": p.risk_level,
                        "risk_score": p.risk_score,
                        "predicted_count": p.predicted_migrant_count,
                        "factors": p.contributing_factors
                    }
                })
        return {"type": "FeatureCollection", "features": features}