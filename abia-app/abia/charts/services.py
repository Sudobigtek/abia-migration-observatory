from django.db.models import Count, Avg, Sum, Q
from datetime import datetime, timedelta
from .models import ChartDashboard

class ChartService:
    # --- CORE MIGRATION DATA ---
    @staticmethod
    def get_migrant_trends(days=30):
        from abia.migrants.models import Migrant
        end = datetime.now().date()
        start = end - timedelta(days=days)
        data = Migrant.objects.filter(
            created_at__date__range=[start, end]
        ).extra(select={"day": "DATE(created_at)"}).values("day").annotate(
            count=Count("id")
        ).order_by("day")
        return {"labels": [d["day"] for d in data], "data": [d["count"] for d in data]}

    @staticmethod
    def get_cases_by_status():
        from abia.cases.models import Case
        data = Case.objects.values("status").annotate(count=Count("id")).order_by("-count")
        return {"labels": [d["status"] for d in data], "data": [d["count"] for d in data]}

    @staticmethod
    def get_migrants_by_lga():
        from abia.migrants.models import Migrant
        data = Migrant.objects.values("current_lga__name").annotate(
            count=Count("id")
        ).order_by("-count")[:20]
        return {"labels": [d["current_lga__name"] or "Unknown" for d in data],
                "data": [d["count"] for d in data]}

    @staticmethod
    def get_referral_completion_rate():
        from abia.referrals.models import Referral
        total = Referral.objects.count()
        completed = Referral.objects.filter(status="completed").count()
        pending = Referral.objects.filter(status="pending").count()
        return {"labels": ["Completed", "Pending", "Other"],
                "data": [completed, pending, total - completed - pending]}

    # --- CBN REMITTANCE DATA ---
    @staticmethod
    def get_remittances_by_lga():
        from abia.cbn.models import RemittanceRecord
        data = RemittanceRecord.objects.filter(status="completed").values(
            "recipient_lga__name"
        ).annotate(total=Sum("naira_equivalent")).order_by("-total")[:15]
        return {"labels": [d["recipient_lga__name"] or "Unknown" for d in data],
                "data": [float(d["total"] or 0) for d in data]}

    @staticmethod
    def get_remittances_by_channel():
        from abia.cbn.models import RemittanceRecord
        data = RemittanceRecord.objects.filter(status="completed").values(
            "channel"
        ).annotate(total=Sum("naira_equivalent")).order_by("-total")
        return {"labels": [d["channel"] for d in data],
                "data": [float(d["total"] or 0) for d in data]}

    @staticmethod
    def get_remittance_trends():
        from abia.cbn.models import RemittanceRecord
        from django.db.models.functions import TruncMonth
        data = RemittanceRecord.objects.filter(status="completed").annotate(
            month=TruncMonth("transaction_date")
        ).values("month").annotate(total=Sum("naira_equivalent")).order_by("month")
        return {"labels": [str(d["month"]) for d in data],
                "data": [float(d["total"] or 0) for d in data]}

    # --- WTO TRADE DATA ---
    @staticmethod
    def get_trade_balance():
        from abia.wto.models import TradeRecord
        exports = TradeRecord.objects.filter(flow_type="export").values("sector").annotate(
            total=Sum("value_usd"))
        imports = TradeRecord.objects.filter(flow_type="import").values("sector").annotate(
            total=Sum("value_usd"))
        exp_map = {e["sector"]: float(e["total"] or 0) for e in exports}
        imp_map = {i["sector"]: float(i["total"] or 0) for i in imports}
        sectors = sorted(set(list(exp_map.keys()) + list(imp_map.keys())))
        return {"labels": sectors,
                "datasets": [
                    {"label": "Exports", "data": [exp_map.get(s, 0) for s in sectors]},
                    {"label": "Imports", "data": [imp_map.get(s, 0) for s in sectors]},
                ]}

    @staticmethod
    def get_labour_intensive_trade():
        from abia.wto.models import TradeRecord
        data = TradeRecord.objects.filter(labour_intensity_score__gte=60).values(
            "sector"
        ).annotate(total=Sum("value_usd")).order_by("-total")
        return {"labels": [d["sector"] for d in data],
                "data": [float(d["total"] or 0) for d in data]}

    # --- ECOWAS DATA ---
    @staticmethod
    def get_ecowas_corridors():
        from abia.ecowas.models import ECOWASMigrantFlow
        data = ECOWASMigrantFlow.objects.values(
            "country_of_origin", "country_of_destination"
        ).annotate(total=Sum("estimated_count")).order_by("-total")[:10]
        return {"labels": [f"{d['country_of_origin']} -> {d['country_of_destination']}" for d in data],
                "data": [d["total"] for d in data]}

    @staticmethod
    def get_ecowas_free_movement():
        from abia.ecowas.models import ECOWASMigrantFlow
        data = ECOWASMigrantFlow.objects.filter(migration_type="labour").values(
            "gender"
        ).annotate(count=Sum("estimated_count"))
        return {"labels": [d["gender"] or "Unknown" for d in data],
                "data": [d["count"] for d in data]}

    # --- WORLD BANK DATA ---
    @staticmethod
    def get_wb_remittance_indicators():
        from abia.worldbank.models import WBDataPoint, WBIndicator
        ind = WBIndicator.objects.filter(category="remittance", is_active=True).first()
        if not ind:
            return {"labels": [], "data": []}
        points = ind.data_points.filter(country_code="NGA").values("year", "value").order_by("year")
        return {"labels": [d["year"] for d in points],
                "data": [float(d["value"] or 0) for d in points]}

    # --- SPORTS DATA ---
    @staticmethod
    def get_sports_by_destination():
        from abia.sports.models import AthleteTransfer
        data = AthleteTransfer.objects.filter(status="completed", is_international=True).values(
            "to_country"
        ).annotate(count=Count("id"), total=Sum("transfer_fee_usd")).order_by("-count")[:10]
        return {"labels": [d["to_country"] for d in data],
                "data": [d["count"] for d in data]}

    @staticmethod
    def get_sports_talent_value():
        from abia.sports.models import AthleteTransfer
        data = AthleteTransfer.objects.filter(status="completed", is_international=True).values(
            "transfer_type"
        ).annotate(total=Sum("transfer_fee_usd")).order_by("-total")
        return {"labels": [d["transfer_type"] for d in data],
                "data": [float(d["total"] or 0) for d in data]}

    @staticmethod
    def get_sports_lga_map():
        from abia.sports.models import AthleteProfile
        data = AthleteProfile.objects.filter(is_active=True).values(
            "origin_lga__name"
        ).annotate(count=Count("id")).order_by("-count")[:15]
        return {"labels": [d["origin_lga__name"] or "Unknown" for d in data],
                "data": [d["count"] for d in data]}

    # --- MASTER BUILDER ---
    @staticmethod
    def build_chart_data(dashboard):
        source = dashboard.data_source
        if source == "migrants":
            return ChartService.get_migrants_by_lga()
        elif source == "cases":
            return ChartService.get_cases_by_status()
        elif source == "referrals":
            return ChartService.get_referral_completion_rate()
        elif source == "trends":
            return ChartService.get_migrant_trends()
        elif source == "remittances_by_lga":
            return ChartService.get_remittances_by_lga()
        elif source == "remittances_by_channel":
            return ChartService.get_remittances_by_channel()
        elif source == "remittance_trends":
            return ChartService.get_remittance_trends()
        elif source == "trade_balance":
            return ChartService.get_trade_balance()
        elif source == "labour_intensive_trade":
            return ChartService.get_labour_intensive_trade()
        elif source == "ecowas_corridors":
            return ChartService.get_ecowas_corridors()
        elif source == "ecowas_free_movement":
            return ChartService.get_ecowas_free_movement()
        elif source == "wb_remittance_indicators":
            return ChartService.get_wb_remittance_indicators()
        elif source == "sports_destinations":
            return ChartService.get_sports_by_destination()
        elif source == "sports_talent_value":
            return ChartService.get_sports_talent_value()
        elif source == "sports_lga_map":
            return ChartService.get_sports_lga_map()
        return {"labels": [], "data": []}

    @staticmethod
    def get_unified_summary():
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        from abia.referrals.models import Referral
        from abia.hotspot.models import HotspotPrediction
        from abia.cbn.models import RemittanceRecord
        from abia.sports.models import AthleteTransfer
        return {
            "total_migrants": Migrant.objects.count(),
            "total_cases": Case.objects.count(),
            "open_cases": Case.objects.filter(status="open").count(),
            "total_referrals": Referral.objects.count(),
            "critical_hotspots": HotspotPrediction.objects.filter(risk_level="critical").count(),
            "total_remittances_ngn": float(RemittanceRecord.objects.filter(status="completed").aggregate(
                total=Sum("naira_equivalent"))["total"] or 0),
            "total_sports_transfer_value_usd": float(AthleteTransfer.objects.filter(
                status="completed", is_international=True).aggregate(
                total=Sum("transfer_fee_usd"))["total"] or 0),
            "charts": ChartService.get_migrants_by_lga(),
        }