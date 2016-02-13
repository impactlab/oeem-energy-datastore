from rest_framework import serializers

from . import models

class ProjectOwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectOwner
        fields = ( 'id', 'user')


class ProjectSerializer(serializers.ModelSerializer):

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
        )


class DailyUsageBaselineSerializer(serializers.ModelSerializer):
    value = serializers.FloatField(source='value_clean')

    class Meta:
        model = models.DailyUsageBaseline
        fields = ('date', 'value',)


class DailyUsageReportingSerializer(serializers.ModelSerializer):
    value = serializers.FloatField(source='value_clean')

    class Meta:
        model = models.DailyUsageReporting
        fields = ('date', 'value',)


class MonthlyAverageUsageBaselineSerializer(serializers.ModelSerializer):
    value = serializers.FloatField(source='value_clean')

    class Meta:
        model = models.MonthlyAverageUsageBaseline
        fields = ('date', 'value',)


class MonthlyAverageUsageReportingSerializer(serializers.ModelSerializer):
    value = serializers.FloatField(source='value_clean')

    class Meta:
        model = models.MonthlyAverageUsageReporting
        fields = ('date', 'value',)


class MeterRunSerializer(serializers.ModelSerializer):
    annual_usage_baseline = serializers.FloatField(source='annual_usage_baseline_clean')
    annual_usage_reporting = serializers.FloatField(source='annual_usage_reporting_clean')
    annual_savings = serializers.FloatField(source='annual_savings_clean')
    gross_savings = serializers.FloatField(source='gross_savings_clean')
    cvrmse_baseline = serializers.FloatField(source='cvrmse_baseline_clean')
    cvrmse_reporting = serializers.FloatField(source='cvrmse_reporting_clean')

    dailyusagebaseline_set = DailyUsageBaselineSerializer(many=True)
    dailyusagereporting_set = DailyUsageReportingSerializer(many=True)

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
    annual_usage_baseline = serializers.FloatField(source='annual_usage_baseline_clean')
    annual_usage_reporting = serializers.FloatField(source='annual_usage_reporting_clean')
    annual_savings = serializers.FloatField(source='annual_savings_clean')
    gross_savings = serializers.FloatField(source='gross_savings_clean')
    cvrmse_baseline = serializers.FloatField(source='cvrmse_baseline_clean')
    cvrmse_reporting = serializers.FloatField(source='cvrmse_reporting_clean')

    class Meta:
        model = models.MeterRun
        fields = (
            'project',
            'annual_usage_baseline',
            'annual_usage_reporting',
            'gross_savings',
            'annual_savings',
            'cvrmse_baseline',
            'cvrmse_reporting',
            'fuel_type',
        )


class MeterRunDailySerializer(serializers.ModelSerializer):
    annual_usage_baseline = serializers.FloatField(source='annual_usage_baseline_clean')
    annual_usage_reporting = serializers.FloatField(source='annual_usage_reporting_clean')
    annual_savings = serializers.FloatField(source='annual_savings_clean')
    gross_savings = serializers.FloatField(source='gross_savings_clean')
    cvrmse_baseline = serializers.FloatField(source='cvrmse_baseline_clean')
    cvrmse_reporting = serializers.FloatField(source='cvrmse_reporting_clean')

    dailyusagebaseline_set = DailyUsageBaselineSerializer(many=True)
    dailyusagereporting_set = DailyUsageReportingSerializer(many=True)

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
    annual_usage_baseline = serializers.FloatField(source='annual_usage_baseline_clean')
    annual_usage_reporting = serializers.FloatField(source='annual_usage_reporting_clean')
    annual_savings = serializers.FloatField(source='annual_savings_clean')
    gross_savings = serializers.FloatField(source='gross_savings_clean')

    monthlyaverageusagebaseline_set = MonthlyAverageUsageBaselineSerializer(many=True)
    monthlyaverageusagereporting_set = MonthlyAverageUsageReportingSerializer(many=True)

    class Meta:
        model = models.MeterRun
        fields = (
            'project',
            'annual_usage_baseline',
            'annual_usage_reporting',
            'gross_savings',
            'annual_savings',
            'monthlyaverageusagebaseline_set',
            'monthlyaverageusagereporting_set',
            'fuel_type',
        )


class ConsumptionRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ConsumptionRecord
        fields = ('id', 'start', 'value', 'estimated')


class ConsumptionMetadataSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ConsumptionMetadata
        fields = ('id', 'fuel_type', 'energy_unit', 'project')


class ConsumptionMetadataSerializer(serializers.ModelSerializer):

    records = ConsumptionRecordSerializer(many=True)

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


class ProjectBlockSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectBlock
        fields = ( 'id', 'name', 'project_owner', 'projects')


class ProjectBlockNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectBlock
        fields = ( 'id', 'name')


class ProjectBlockMonthlyTimeseriesSerializer(serializers.ModelSerializer):

    recent_summaries = FuelTypeSummaryMonthlyTimeseriesSerializer(many=True, read_only=True)

    class Meta:
        model = models.ProjectBlock
        fields = (
            'id',
            'name',
            'project_owner',
            'projects',
            'recent_summaries',
        )


class ProjectAttributeKeySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectAttributeKey
        fields = (
            'id',
            'name',
            'display_name',
            'data_type'
        )


class ProjectAttributeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectAttribute
        fields = (
            'id',
            'project',
            'key',
            'value',
            'boolean_value',
            'char_value',
            'date_value',
            'datetime_value',
            'float_value',
            'integer_value',
        )


class ProjectAttributeValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectAttribute
        fields = (
            'id',
            'key',
            'project',
            'value',
        )


class ProjectAttributeValueEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectAttribute
        fields = (
            'key',
            'value',
        )


class ProjectWithAttributesSerializer(serializers.ModelSerializer):

    attributes = ProjectAttributeValueEmbeddedSerializer(many=True, read_only=True)

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
            'attributes',
        )

class ProjectWithMeterRunsSerializer(serializers.ModelSerializer):

    recent_meter_runs = MeterRunSummarySerializer(many=True, read_only=True)

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
            'recent_meter_runs',
        )

class ProjectWithAttributesAndMeterRunsSerializer(serializers.ModelSerializer):

    recent_meter_runs = MeterRunSummarySerializer(many=True, read_only=True)
    attributes = ProjectAttributeValueEmbeddedSerializer(many=True, read_only=True)

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
            'recent_meter_runs',
            'attributes',
        )

class ProjectWithMonthlyMeterRunsSerializer(serializers.ModelSerializer):

    recent_meter_runs = MeterRunMonthlySerializer(many=True, read_only=True)

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
            'recent_meter_runs',
        )
