from django.db.models import Sum, Q
from .models import TradeRecord

class TradeRecordRepository:
    @staticmethod
    def get_by_year(year):
        qs = TradeRecord.objects.all()
        if year:
            qs = qs.filter(year=year)
        return qs

    @staticmethod
    def get_trade_balance_by_sector(year=None):
        qs = TradeRecordRepository.get_by_year(year)
        exports = qs.filter(flow_type="export").values("sector").annotate(total=Sum("value_usd"))
        imports = qs.filter(flow_type="import").values("sector").annotate(total=Sum("value_usd"))
        exp_map = {e["sector"]: e["total"] for e in exports}
        imp_map = {i["sector"]: i["total"] for i in imports}
        sectors = set(list(exp_map.keys()) + list(imp_map.keys()))
        return [{"sector": s, "exports": exp_map.get(s, 0), "imports": imp_map.get(s, 0),
                 "balance": exp_map.get(s, 0) - imp_map.get(s, 0)} for s in sectors]

    @staticmethod
    def get_top_partners(flow_type="export", year=None, limit=10):
        qs = TradeRecord.objects.filter(flow_type=flow_type)
        if year:
            qs = qs.filter(year=year)
        return list(qs.values("trade_partner").annotate(total=Sum("value_usd")).order_by("-total")[:limit])

    @staticmethod
    def get_labour_intensive_trade(year=None):
        qs = TradeRecord.objects.filter(labour_intensity_score__gte=60)
        if year:
            qs = qs.filter(year=year)
        return list(qs.values("sector", "flow_type").annotate(total=Sum("value_usd")).order_by("-total"))

    @staticmethod
    def get_yearly_summary():
        return list(TradeRecord.objects.values("year").annotate(
            exports=Sum("value_usd", filter=Q(flow_type="export")),
            imports=Sum("value_usd", filter=Q(flow_type="import"))
        ).order_by("year"))