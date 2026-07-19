import uuid
from django.db import models
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex

class SearchIndex(models.Model):
    """Unified search index across all entities."""
    ENTITY_TYPES = [
        ('migrant', 'Migrant'),
        ('case', 'Case'),
        ('referral', 'Referral'),
        ('document', 'Document'),
        ('lga', 'LGA'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    search_vector = SearchVectorField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.entity_type}: {self.title}"
    
    def update_search_vector(self):
        """Update the search vector from title + content."""
        self.search_vector = (
            SearchVector('title', weight='A') +
            SearchVector('content', weight='B')
        )
        self.save(update_fields=['search_vector'])
