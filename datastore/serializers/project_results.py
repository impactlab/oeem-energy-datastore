from rest_framework import serializers

from .. import models

__all__ = (
    'ProjectResultSerializer',
)


class ModelingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModelingPeriod
        fields = (
            'id',
            'interpretation',
            'start_date',
            'end_date'
        )


class ModelingPeriodGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModelingPeriodGroup
        fields = (
            'id',
            'baseline_period',
            'reporting_period',
        )


class DerivativeAggregationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DerivativeAggregation
        fields = (
            'id',
            'modeling_period_group',
            'trace_interpretation',
            'interpretation',
            'baseline_value',
            'baseline_upper',
            'baseline_lower',
            'baseline_n',
            'reporting_value',
            'reporting_upper',
            'reporting_lower',
            'reporting_n',
        )


class DerivativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Derivative
        fields = (
            'id',
            'interpretation',
            'value',
            'upper',
            'lower',
            'n',
        )


class EnergyTraceModelResultSerializer(serializers.ModelSerializer):
    derivatives = DerivativeSerializer(many=True, read_only=True)

    class Meta:
        model = models.EnergyTraceModelResult
        fields = (
            'id',
            'project_result',
            'energy_trace',
            'modeling_period',
            'derivatives',
            'status',
            'r2',
            'rmse',
            'cvrmse',
            'model_serializiation',
            'upper',
            'lower',
            'n',
        )


class ProjectResultSerializer(serializers.ModelSerializer):
    modeling_periods = ModelingPeriodSerializer(many=True, read_only=True)
    modeling_period_groups = ModelingPeriodGroupSerializer(
        many=True, read_only=True)
    derivative_aggregations = DerivativeAggregationSerializer(
        many=True, read_only=True)
    energy_trace_model_results = EnergyTraceModelResultSerializer(
        many=True, read_only=True)

    class Meta:
        model = models.ProjectResult
        fields = (
            'id',
            'project',
            'eemeter_version',
            'meter_class',
            'meter_settings',
            'modeling_periods',
            'modeling_period_groups',
            'derivative_aggregations',
            'energy_trace_model_results',
            'added',
            'updated',
        )
