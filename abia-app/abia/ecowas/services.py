from django.db.models import Sum, Count, Q
from .models import ECOWASMigrantFlow, ECOWASTradeFlow

class ECOWASService:
    @staticmethod
    def get_migration_by_corridor():
        data = ECOWASMigrantFlow.objects.values(
            "country_of_origin", "country_of_destination"
        ).annotate(total=Sum("estimated_count")).order_by("-total")[:20]
        return list(data)

    @staticmethod
    def get_migration_by_sector(year=None):
        qs = ECOWASMigrantFlow.objects.all()
        if year:
            qs = qs.filter(year=year)
        return list(qs.values("sector").annotate(total=Sum("estimated_count")).order_by("-total"))

    @staticmethod
    def get_free_movement_stats(year=None):
        qs = ECOWASMigrantFlow.objects.filter(migration_type="labour")
        if year:
            qs = qs.filter(year=year)
        total = qs.aggregate(total=Sum("estimated_count"))["total"] or 0
        by_gender = list(qs.values("gender").annotate(count=Sum("estimated_count")))
        return {"total_labour_migrants": total, "by_gender": by_gender}

    @staticmethod
    def get_intra_regional_trade(year=None):
        qs = ECOWASTradeFlow.objects.all()
        if year:
            qs = qs.filter(year=year)
        total_exports = qs.aggregate(total=Sum("export_value"))["total"] or 0
        total_imports = qs.aggregate(total=Sum("import_value"))["total"] or 0
        top_partners = list(qs.values("partner_country").annotate(
            exports=Sum("export_value"), imports=Sum("import_value")
        ).order_by("-exports")[:10])
        return {"total_exports": total_exports, "total_imports": total_imports, "top_partners": top_partners}