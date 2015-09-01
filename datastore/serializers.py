from rest_framework import serializers
from .models import ConsumptionRecord
from .models import ConsumptionMetadata

class ConsumptionRecordEmbeddedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumptionRecord
        fields = ('id', 'start', 'value', 'estimated')

class ConsumptionMetadataSerializer(serializers.ModelSerializer):
    records = ConsumptionRecordEmbeddedSerializer(many=True)

    class Meta:
        model = ConsumptionMetadata
        fields = ('id', 'fuel_type', 'fuel_unit', 'records')

    def create(self, validated_data):
        records_data = validated_data.pop('records')
        consumption_metadata = ConsumptionMetadata.objects.create(**validated_data)
        for record_data in records_data:
            ConsumptionRecord.objects.create(metadata=consumption_metadata, **record_data)
        return consumption_metadata
