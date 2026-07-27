"""NBS-compliant data serializers."""
from rest_framework import serializers


class NBSMigrationRecordSerializer(serializers.Serializer):
    """NBS-standard migration record format."""
    name_of_migrant = serializers.CharField()
    date_of_birth = serializers.DateField(required=False)
    lga_of_residence = serializers.CharField()
    destination_country = serializers.CharField(required=False)
    isco_code = serializers.CharField(required=False)
    departure_date = serializers.DateField(required=False)
