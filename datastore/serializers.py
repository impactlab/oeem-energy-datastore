from rest_framework import serializers

from . import models

class ProjectBlockEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectBlock
        fields = ( 'id', 'name', 'project_owner')


class ProjectSerializer(serializers.ModelSerializer):
    recent_meter_runs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    consumptionmetadata_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    projectblock_set = ProjectBlockEmbeddedSerializer(many=True, read_only=True)

    class Meta:
        model = models.Project
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
            'longitude',
            'consumptionmetadata_set',
            'recent_meter_runs',
            'projectblock_set',
        )


class DailyUsageBaselineEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DailyUsageBaseline
        fields = ('date', 'value',)


class DailyUsageReportingEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DailyUsageReporting
        fields = ('date', 'value',)


class MonthlyAverageUsageBaselineEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MonthlyAverageUsageBaseline
        fields = ('date', 'value',)


class MonthlyAverageUsageReportingEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MonthlyAverageUsageReporting
        fields = ('date', 'value',)


class MeterRunSerializer(serializers.ModelSerializer):
    dailyusagebaseline_set = DailyUsageBaselineEmbeddedSerializer(many=True)
    dailyusagereporting_set = DailyUsageReportingEmbeddedSerializer(many=True)

    class Meta:
        model = models.MeterRun
        fields = (
            'project',
            'consumption_metadata',
            'serialization',
            'annual_usage_baseline',
            'annual_usage_reporting',
            'gross_savings',
            'annual_savings',
            'meter_type',
            'model_parameter_json_baseline',
            'model_parameter_json_reporting',
            'cvrmse_baseline',
            'cvrmse_reporting',
            'dailyusagebaseline_set',
            'dailyusagereporting_set',
            'fuel_type',
        )


class MeterRunSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MeterRun
        fields = (
            'project',
            'consumption_metadata',
            'annual_usage_baseline',
            'annual_usage_reporting',
            'gross_savings',
            'annual_savings',
            'meter_type',
            'model_parameter_json_baseline',
            'model_parameter_json_reporting',
            'cvrmse_baseline',
            'cvrmse_reporting',
            'fuel_type',
        )


class MeterRunDailySerializer(serializers.ModelSerializer):
    dailyusagebaseline_set = DailyUsageBaselineEmbeddedSerializer(many=True)
    dailyusagereporting_set = DailyUsageReportingEmbeddedSerializer(many=True)

    class Meta:
        model = models.MeterRun
        fields = (
            'project',
            'consumption_metadata',
            'annual_usage_baseline',
            'annual_usage_reporting',
            'gross_savings',
            'annual_savings',
            'meter_type',
            'model_parameter_json_baseline',
            'model_parameter_json_reporting',
            'cvrmse_baseline',
            'cvrmse_reporting',
            'dailyusagebaseline_set',
            'dailyusagereporting_set',
            'fuel_type',
        )


class MeterRunMonthlySerializer(serializers.ModelSerializer):
    monthlyaverageusagebaseline_set = MonthlyAverageUsageBaselineEmbeddedSerializer(many=True)
    monthlyaverageusagereporting_set = MonthlyAverageUsageReportingEmbeddedSerializer(many=True)

    class Meta:
        model = models.MeterRun
        fields = (
            'project',
            'consumption_metadata',
            'annual_usage_baseline',
            'annual_usage_reporting',
            'gross_savings',
            'annual_savings',
            'meter_type',
            'model_parameter_json_baseline',
            'model_parameter_json_reporting',
            'cvrmse_baseline',
            'cvrmse_reporting',
            'monthlyaverageusagebaseline_set',
            'monthlyaverageusagereporting_set',
            'fuel_type',
        )


class ConsumptionRecordEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ConsumptionRecord
        fields = ('id', 'start', 'value', 'estimated')


class ConsumptionMetadataSerializer(serializers.ModelSerializer):

    records = ConsumptionRecordEmbeddedSerializer(many=True)

    class Meta:
        model = models.ConsumptionMetadata
        fields = ('id', 'fuel_type', 'energy_unit', 'records', 'project')

    def create(self, validated_data):
        records_data = validated_data.pop('records')

        consumption_metadata = \
                models.ConsumptionMetadata.objects.create(**validated_data)

        for record_data in records_data:
            models.ConsumptionRecord.objects.create(metadata=consumption_metadata,
                    **record_data)

        return consumption_metadata


class ProjectIdEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = ('id',)


class ProjectBlockSerializer(serializers.ModelSerializer):

    project = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.ProjectBlock
        fields = ( 'id', 'name', 'project_owner', 'project')


class MonthlyUsageSummaryBaselineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MonthlyUsageSummaryBaseline
        fields = ( 'id', 'value', 'date')


class MonthlyUsageSummaryActualSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MonthlyUsageSummaryActual
        fields = ( 'id', 'value', 'date', 'n_projects')


class FuelTypeSummaryMonthlyTimeseriesSerializer(serializers.ModelSerializer):

    monthlyusagesummarybaseline_set = MonthlyUsageSummaryBaselineSerializer(many=True, read_only=True)
    monthlyusagesummaryactual_set = MonthlyUsageSummaryActualSerializer(many=True, read_only=True)

    class Meta:
        model = models.FuelTypeSummary
        fields = (
            'id',
            'fuel_type',
            'monthlyusagesummarybaseline_set',
            'monthlyusagesummaryactual_set',
        )


class ProjectBlockMonthlyTimeseriesSerializer(serializers.ModelSerializer):

    project = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    recent_summaries = FuelTypeSummaryMonthlyTimeseriesSerializer(many=True, read_only=True)

    class Meta:
        model = models.ProjectBlock
        fields = (
            'id',
            'name',
            'project_owner',
            'project',
            'recent_summaries',
        )


class ProjectAttributeKeySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectAttributeKey
        fields = (
            'name',
            'data_type',
        )

class ProjectAttributeKeySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectAttributeKey
        fields = (
            'project',
            'name',
            'value',
        )
