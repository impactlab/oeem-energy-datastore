from rest_framework import serializers
from .models import ProjectOwner
from .models import Project
from .models import Block
from .models import ConsumptionMetadata
from .models import ConsumptionRecord
from .models import MeterRun
from .models import DailyUsageBaseline
from .models import DailyUsageReporting
from .models import AnnualUsageBaseline
from .models import AnnualUsageReporting
from .models import GrossSavings
from .models import AnnualSavings
from .models import ModelType
from .models import ModelParameters

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'project_owner', 'project_id')

class ConsumptionRecordEmbeddedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumptionRecord
        fields = ('id', 'start', 'value', 'estimated')

class ConsumptionMetadataSerializer(serializers.ModelSerializer):
    records = ConsumptionRecordEmbeddedSerializer(many=True)

    class Meta:
        model = ConsumptionMetadata
        fields = ('id', 'fuel_type', 'energy_unit', 'records')

    def create(self, validated_data):
        records_data = validated_data.pop('records')
        consumption_metadata = ConsumptionMetadata.objects.create(**validated_data)
        for record_data in records_data:
            ConsumptionRecord.objects.create(metadata=consumption_metadata, **record_data)
        return consumption_metadata
