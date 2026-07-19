from celery import shared_task
from .models import SearchIndex

@shared_task
def auto_reindex_migrant(migrant_id):
    """Auto-reindex a single migrant when created/updated."""
    from abia.migrants.models import Migrant
    try:
        migrant = Migrant.objects.get(id=migrant_id)
        content = f"{migrant.full_name} {migrant.phone or ''} {migrant.email or ''}"
        obj, _ = SearchIndex.objects.update_or_create(
            entity_type='migrant',
            entity_id=migrant.id,
            defaults={
                'title': migrant.full_name,
                'content': content,
                'metadata': {
                    'status': migrant.status,
                    'gender': migrant.gender,
                    'lga': migrant.current_lga.name if migrant.current_lga else None,
                }
            }
        )
        obj.update_search_vector()
        return {'status': 'indexed', 'entity': 'migrant', 'id': str(migrant_id)}
    except Migrant.DoesNotExist:
        return {'status': 'not_found', 'id': str(migrant_id)}
