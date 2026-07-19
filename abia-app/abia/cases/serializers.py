"""
ABIA Migration Observatory — Cases API Serializers
NASA-level: explicit fields, nested relations, workflow validation.
"""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point

from abia.cases.models import Case
from abia.referrals.models import Referral
from abia.migrants.serializers import MigrantListSerializer


class CaseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for case lists."""
    migrant_name = serializers.CharField(source="migrant.full_name", read_only=True)
    migrant_id = serializers.UUIDField(source="migrant.id", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    referral_count = serializers.IntegerField(source="referrals.count", read_only=True)
    days_open = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = [
            "id", "migrant_id", "migrant_name",
            "case_type", "status", "priority",
            "assigned_to_name", "lga_name",
            "referral_count", "days_open",
            "created_at", "updated_at", "resolved_at",
        ]

    def get_days_open(self, obj):
        from datetime import datetime
        if obj.resolved_at:
            return (obj.resolved_at - obj.created_at).days
        return (datetime.now(obj.created_at.tzinfo) - obj.created_at).days


class CaseDetailSerializer(GeoFeatureModelSerializer):
    """Full case serializer with GeoJSON support."""
    migrant = MigrantListSerializer(read_only=True)
    migrant_id = serializers.UUIDField(write_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    assigned_to_id = serializers.UUIDField(source="assigned_to.id", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    lga_id = serializers.UUIDField(source="lga.id", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    referrals = serializers.SerializerMethodField()
    location_geojson = serializers.SerializerMethodField()
    days_open = serializers.SerializerMethodField()

    class Meta:
        model = Case
        geo_field = "location"
        fields = [
            "id", "migrant", "migrant_id",
            "case_type", "description", "status", "priority",
            "assigned_to_id", "assigned_to_name",
            "lga_id", "lga_name",
            "location", "location_geojson",
            "documents",
            "created_by_name", "created_at", "updated_at", "resolved_at",
            "referrals", "days_open",
        ]

    def get_referrals(self, obj):
        from abia.referrals.serializers import ReferralListSerializer
        referrals = obj.referrals.all()[:10]  # Limit nested data
        return ReferralListSerializer(referrals, many=True).data

    def get_location_geojson(self, obj):
        if obj.location:
            return {"type": "Point", "coordinates": [obj.location.x, obj.location.y]}
        return None

    def get_days_open(self, obj):
        from datetime import datetime
        if obj.resolved_at:
            return (obj.resolved_at - obj.created_at).days
        return (datetime.now(obj.created_at.tzinfo) - obj.created_at).days

    def validate(self, data):
        # Workflow validation
        status = data.get("status", getattr(self.instance, "status", "open") if self.instance else "open")

        if status == "resolved" and not data.get("resolved_at"):
            from datetime import timezone, datetime
            data["resolved_at"] = datetime.now(timezone.utc)

        if status != "resolved" and "resolved_at" in data:
            data["resolved_at"] = None

        return data

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class CaseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create/update with lat/lon support."""
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Case
        fields = [
            "id", "migrant", "case_type", "description",
            "status", "priority", "assigned_to", "lga",
            "latitude", "longitude", "documents",
        ]

    def validate(self, data):
        lat = data.pop("latitude", None)
        lon = data.pop("longitude", None)
        if lat is not None and lon is not None:
            data["location"] = Point(lon, lat, srid=4326)

        # Workflow: set resolved_at if status is resolved
        if data.get("status") == "resolved" and not data.get("resolved_at"):
            from datetime import timezone, datetime
            data["resolved_at"] = datetime.now(timezone.utc)

        return data

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class CaseStatsSerializer(serializers.Serializer):
    """Aggregate statistics serializer."""
    total_cases = serializers.IntegerField()
    by_status = serializers.DictField()
    by_type = serializers.DictField()
    by_priority = serializers.DictField()
    by_lga = serializers.DictField()
    avg_resolution_days = serializers.FloatField()
    open_cases = serializers.IntegerField()
    critical_cases = serializers.IntegerField()
