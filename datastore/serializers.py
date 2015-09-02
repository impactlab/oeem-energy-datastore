from rest_framework import serializers
from .models import Project
# from .models import ProjectBlock
from .models import ConsumptionMetadata
from .models import ConsumptionRecord
# from .models import MeterRun
# from .models import DailyUsageBaseline
# from .models import DailyUsageReporting
# from .models import ModelType

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
                'id',
                'project_owner',
                'project_id',
                'baseline_period_start',
                'baseline_period_end',
                'reporting_period_start',
                'reporting_period_end',
                'zipcode',
                'weather_station',
                'latitude',
                'longitude')

class ConsumptionRecordEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsumptionRecord
        fields = ('id', 'start', 'value', 'estimated')

class ConsumptionMetadataSerializer(serializers.ModelSerializer):
    records = ConsumptionRecordEmbeddedSerializer(many=True)

    class Meta:
        model = ConsumptionMetadata
        fields = ('id', 'fuel_type', 'energy_unit', 'records', 'project')

    def create(self, validated_data):
        records_data = validated_data.pop('records')

        consumption_metadata = \
                ConsumptionMetadata.objects.create(**validated_data)

        for record_data in records_data:
            ConsumptionRecord.objects.create(metadata=consumption_metadata,
                    **record_data)

        return consumption_metadata
