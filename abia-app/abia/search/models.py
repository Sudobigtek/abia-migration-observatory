import uuid
from django.db import models

class SearchIndex(models.Model):
    ENTITY_TYPES = [
        ("migrant", "Migrant"),
        ("case", "Case"),
        ("referral", "Referral"),
        ("lga", "LGA"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    lga_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["entity_type", "title"]),
            models.Index(fields=["lga_id"]),
            models.Index(fields=["content"]),
        ]

    def __str__(self):
        return f"{self.entity_type}: {self.title}"