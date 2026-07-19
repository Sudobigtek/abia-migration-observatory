"""
ABIA Migration Observatory — Referrals API Serializers
"""

from rest_framework import serializers

from abia.referrals.models import Referral
from abia.cases.serializers import CaseListSerializer


class ReferralListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for referral lists."""
    case_id = serializers.UUIDField(source="case.id", read_only=True)
    case_type = serializers.CharField(source="case.case_type", read_only=True)
    migrant_name = serializers.CharField(source="case.migrant.full_name", read_only=True)
    from_lga_name = serializers.CharField(source="from_lga.name", read_only=True)
    to_lga_name = serializers.CharField(source="to_lga.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    days_pending = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = [
            "id", "case_id", "case_type", "migrant_name",
            "from_lga_name", "to_lga_name",
            "to_organization", "to_contact_name",
            "status", "days_pending",
            "created_by_name", "created_at", "updated_at",
        ]

    def get_days_pending(self, obj):
        from datetime import datetime
        if obj.status in ["pending", "accepted"]:
            return (datetime.now(obj.created_at.tzinfo) - obj.created_at).days
        return 0


class ReferralDetailSerializer(serializers.ModelSerializer):
    """Full referral serializer with nested case data."""
    case = CaseListSerializer(read_only=True)
    case_id = serializers.UUIDField(write_only=True)
    from_lga_name = serializers.CharField(source="from_lga.name", read_only=True)
    to_lga_name = serializers.CharField(source="to_lga.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    days_pending = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = [
            "id", "case", "case_id",
            "from_lga", "from_lga_name",
            "to_lga", "to_lga_name",
            "to_organization", "to_contact_name", "to_contact_phone",
            "reason", "status", "camunda_process_id",
            "documents",
            "created_by_name", "created_at", "updated_at",
            "days_pending",
        ]

    def get_days_pending(self, obj):
        from datetime import datetime
        if obj.status in ["pending", "accepted"]:
            return (datetime.now(obj.created_at.tzinfo) - obj.created_at).days
        return 0

    def validate(self, data):
        from_lga = data.get("from_lga")
        to_lga = data.get("to_lga")
        if from_lga and to_lga and from_lga == to_lga:
            raise serializers.ValidationError({"to_lga": "Referral cannot be to the same LGA."})
        return data

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class ReferralCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create/update operations."""

    class Meta:
        model = Referral
        fields = [
            "id", "case", "from_lga", "to_lga",
            "to_organization", "to_contact_name", "to_contact_phone",
            "reason", "status", "camunda_process_id", "documents",
        ]

    def validate(self, data):
        from_lga = data.get("from_lga")
        to_lga = data.get("to_lga")
        if from_lga and to_lga and from_lga == to_lga:
            raise serializers.ValidationError({"to_lga": "Referral cannot be to the same LGA."})
        return data

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
