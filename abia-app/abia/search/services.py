from django.db.models import Q
from .models import SearchIndex

class SearchService:
    @staticmethod
    def search(query, entity_type=None, lga_id=None, limit=50):
        qs = SearchIndex.objects.all()
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(metadata__icontains=query)
            )
        if entity_type:
            qs = qs.filter(entity_type=entity_type)
        if lga_id:
            qs = qs.filter(lga_id=lga_id)
        return qs[:limit]

    @staticmethod
    def index_migrant(migrant):
        phone = migrant.phone or ""
        email = getattr(migrant, "email", "") or ""
        lga_str = str(migrant.current_lga) if getattr(migrant, "current_lga", None) else ""
        lga_id_str = str(migrant.current_lga.id) if getattr(migrant, "current_lga", None) else ""
        SearchIndex.objects.update_or_create(
            entity_type="migrant",
            entity_id=str(migrant.id),
            defaults={
                "title": migrant.full_name,
                "content": f"{migrant.full_name} {phone} {email}",
                "metadata": {
                    "status": migrant.status,
                    "gender": getattr(migrant, "gender", None),
                    "lga": lga_str,
                },
                "lga_id": lga_id_str,
            }
        )

    @staticmethod
    def index_case(case):
        desc = case.description or ""
        lga_str = str(case.current_lga) if getattr(case, "current_lga", None) else ""
        lga_id_str = str(case.current_lga.id) if getattr(case, "current_lga", None) else ""
        SearchIndex.objects.update_or_create(
            entity_type="case",
            entity_id=str(case.id),
            defaults={
                "title": f"Case {case.case_type}",
                "content": f"{case.case_type} {desc} {case.status}",
                "metadata": {
                    "status": case.status,
                    "priority": getattr(case, "priority", None),
                    "lga": lga_str,
                },
                "lga_id": lga_id_str,
            }
        )

    @staticmethod
    def rebuild_index():
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        SearchIndex.objects.all().delete()
        for m in Migrant.objects.all():
            SearchService.index_migrant(m)
        for c in Case.objects.all():
            SearchService.index_case(c)
        return SearchIndex.objects.count()