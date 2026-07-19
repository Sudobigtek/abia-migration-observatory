from rest_framework import serializers
from .models import SearchIndex

class SearchResultSerializer(serializers.ModelSerializer):
    score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = SearchIndex
        fields = ['id', 'entity_type', 'entity_id', 'title', 'content', 
                  'metadata', 'score', 'created_at']
