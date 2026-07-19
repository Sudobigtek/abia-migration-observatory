"""
ABIA Migration Observatory — Accounts API Serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from abia.accounts.models import LGA

User = get_user_model()


class LGASerializer(serializers.ModelSerializer):
    """LGA serializer with boundary GeoJSON."""
    boundary_geojson = serializers.SerializerMethodField()
    user_count = serializers.IntegerField(source="users.count", read_only=True)
    case_count = serializers.IntegerField(source="cases.count", read_only=True)
    migrant_count = serializers.IntegerField(source="migrants.count", read_only=True)

    class Meta:
        model = LGA
        fields = [
            "id", "name", "code", "boundary", "boundary_geojson",
            "population_2023", "user_count", "case_count", "migrant_count",
            "created_at",
        ]

    def get_boundary_geojson(self, obj):
        if obj.boundary:
            return obj.boundary.geojson
        return None


class UserListSerializer(serializers.ModelSerializer):
    """User list serializer."""
    lga_name = serializers.CharField(source="lga.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "phone", "lga_name", "role", "is_active", "date_joined",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """User detail serializer."""
    lga = LGASerializer(read_only=True)
    assigned_cases_count = serializers.IntegerField(source="assigned_cases.count", read_only=True)
    created_cases_count = serializers.IntegerField(source="cases_created.count", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "phone", "lga", "role", "is_active", "is_staff", "is_superuser",
            "assigned_cases_count", "created_cases_count",
            "date_joined", "last_login",
        ]
