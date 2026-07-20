from rest_framework import serializers
from .models import SearchIndex

class SearchIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchIndex
        fields = ["id", "entity_type", "entity_id", "title", "content", "metadata", "lga_id", "created_at", "updated_at"]