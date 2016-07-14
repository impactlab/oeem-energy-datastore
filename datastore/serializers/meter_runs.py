from rest_framework import serializers

from .. import models

__all__ = (
    'MeterRunSerializer',
    'MeterRunSummarySerializer',
)

MINIMAL_METER_RUN_FIELDS = (
    'id',
    'project',
    'consumption_metadata',
    'meter_class',
    'annual_usage_baseline',
    'annual_usage_reporting',
    'annual_savings',
    'gross_savings',
    'cvrmse_baseline',
    'cvrmse_reporting',
    'valid_meter_run',
    'added',
    'updated',
)

EXTRA_METER_RUN_FIELDS = (
    'interpretation',
    'model_parameter_json_baseline',
    'model_parameter_json_reporting',
)

COMPLETE_METER_RUN_FIELDS = (
    MINIMAL_METER_RUN_FIELDS
    + EXTRA_METER_RUN_FIELDS
    + (
        'serialization',
    )
)

NORMAL_METER_RUN_FIELDS = MINIMAL_METER_RUN_FIELDS + EXTRA_METER_RUN_FIELDS

#
# class MeterRunSerializer(serializers.ModelSerializer):
#     annual_usage_baseline = serializers.FloatField(source='annual_usage_baseline_clean')
#     annual_usage_reporting = serializers.FloatField(source='annual_usage_reporting_clean')
#     annual_savings = serializers.FloatField(source='annual_savings_clean')
#     gross_savings = serializers.FloatField(source='gross_savings_clean')
#     cvrmse_baseline = serializers.FloatField(source='cvrmse_baseline_clean')
#     cvrmse_reporting = serializers.FloatField(source='cvrmse_reporting_clean')
#
#     class Meta:
#         model = models.MeterRun
#         fields = NORMAL_METER_RUN_FIELDS
#
#
# class MeterRunSummarySerializer(serializers.ModelSerializer):
#     annual_usage_baseline = serializers.FloatField(source='annual_usage_baseline_clean')
#     annual_usage_reporting = serializers.FloatField(source='annual_usage_reporting_clean')
#     annual_savings = serializers.FloatField(source='annual_savings_clean')
#     gross_savings = serializers.FloatField(source='gross_savings_clean')
#     cvrmse_baseline = serializers.FloatField(source='cvrmse_baseline_clean')
#     cvrmse_reporting = serializers.FloatField(source='cvrmse_reporting_clean')
#
#     class Meta:
#         model = models.MeterRun
#         fields = MINIMAL_METER_RUN_FIELDS
