"""
ABIA Migration Observatory — Migrants API Serializers
NASA-level design: explicit fields, validation, audit trail support.
"""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point

from abia.migrants.models import Migrant, MigrantVersion, PhotoUploadQueue


class MigrantListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    current_lga_name = serializers.CharField(source="current_lga.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Migrant
        fields = [
            "id", "full_name", "gender", "phone", "email",
            "nationality", "state_of_origin", "current_lga_name",
            "status", "age", "created_at", "updated_at",
            "created_by_name",
        ]

    def get_age(self, obj):
        from datetime import date
        if obj.date_of_birth:
            today = date.today()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None


class MigrantDetailSerializer(GeoFeatureModelSerializer):
    """Full serializer with GeoJSON support for spatial data."""
    current_lga_name = serializers.CharField(source="current_lga.name", read_only=True)
    current_lga_id = serializers.UUIDField(source="current_lga.id", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    created_by_id = serializers.UUIDField(source="created_by.id", read_only=True)
    age = serializers.SerializerMethodField()
    location_geojson = serializers.SerializerMethodField()
    gps_coordinates_geojson = serializers.SerializerMethodField()
    version_count = serializers.IntegerField(source="versions.count", read_only=True)
    pending_photos = serializers.IntegerField(source="photo_queue.count", read_only=True)

    class Meta:
        model = Migrant
        geo_field = "location"
        fields = [
            "id", "odk_submission_id",
            "full_name", "date_of_birth", "gender", "age",
            "phone", "email",
            "id_type", "id_number", "nationality",
            "state_of_origin", "lga_of_origin",
            "current_lga_id", "current_lga_name",
            "current_address", "location", "location_geojson",
            "gps_coordinates", "gps_coordinates_geojson",
            "photo_url", "status",
            "id_number_encrypted", "id_number_plaintext",
            "created_by_id", "created_by_name",
            "created_at", "updated_at",
            "version_count", "pending_photos",
        ]
        extra_kwargs = {
            "id_number_encrypted": {"write_only": True},
            "id_number_plaintext": {"write_only": True},
        }

    def get_age(self, obj):
        from datetime import date
        if obj.date_of_birth:
            today = date.today()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None

    def get_location_geojson(self, obj):
        if obj.location:
            return {
                "type": "Point",
                "coordinates": [obj.location.x, obj.location.y]
            }
        return None

    def get_gps_coordinates_geojson(self, obj):
        if obj.gps_coordinates:
            return {
                "type": "Point",
                "coordinates": [obj.gps_coordinates.x, obj.gps_coordinates.y]
            }
        return None

    def validate_phone(self, value):
        from abia.common.validators import validate_nigeria_phone
        from django.core.exceptions import ValidationError
        if value:
            try:
                validate_nigeria_phone(value)
            except ValidationError as e:
                raise serializers.ValidationError(e.message)
        return value

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class MigrantCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create/update operations."""
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Migrant
        fields = [
            "id", "odk_submission_id",
            "full_name", "date_of_birth", "gender",
            "phone", "email",
            "id_type", "id_number", "nationality",
            "state_of_origin", "lga_of_origin",
            "current_lga", "current_address",
            "latitude", "longitude",
            "photo_url", "status",
            "id_number_plaintext",
        ]

    def validate(self, data):
        # Build Point from lat/lon if provided
        lat = data.pop("latitude", None)
        lon = data.pop("longitude", None)
        if lat is not None and lon is not None:
            data["location"] = Point(lon, lat, srid=4326)
        return data

    def validate_phone(self, value):
        from abia.common.validators import validate_nigeria_phone
        from django.core.exceptions import ValidationError
        if value:
            try:
                validate_nigeria_phone(value)
            except ValidationError as e:
                raise serializers.ValidationError(e.message)
        return value

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class MigrantVersionSerializer(serializers.ModelSerializer):
    """Audit trail serializer."""
    edited_by_name = serializers.CharField(source="edited_by.get_full_name", read_only=True)

    class Meta:
        model = MigrantVersion
        fields = [
            "id", "migrant", "edited_by", "edited_by_name",
            "full_name", "phone", "gender", "current_lga",
            "change_summary", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PhotoUploadQueueSerializer(serializers.ModelSerializer):
    """Photo upload queue serializer."""
    migrant_name = serializers.CharField(source="migrant.full_name", read_only=True)

    class Meta:
        model = PhotoUploadQueue
        fields = [
            "id", "migrant", "migrant_name",
            "photo_path", "retry_count", "status",
            "last_error", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "retry_count"]
