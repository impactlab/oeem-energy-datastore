from rest_framework import serializers

from django.db.models import Manager

# from .meter_runs import (
#     MeterRunSummarySerializer,
# )

from .. import models

__all__ = (
    'ProjectSerializer',
    'ProjectWithAttributesSerializer',
    'ProjectWithMeterRunsSerializer',
    'ProjectWithAttributesAndMeterRunsSerializer',
    'ProjectRunSerializer',
)

BASIC_PROJECT_FIELDS = (
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

def _update_with_recent_meter_runs(data, meter_runs, serializer):

    meter_runs_data = []

    for k, v in meter_runs.items():
        meter_run = serializer.to_representation(v["meter_run"])
        meter_run.update({"interpretation": v["interpretation"]})
        meter_runs_data.append(meter_run)

    data.update({"recent_meter_runs": meter_runs_data})

    return data


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = BASIC_PROJECT_FIELDS


class ProjectAttributeValueEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectAttribute
        fields = (
            'key',
            'value',
        )


class ProjectWithAttributesSerializer(serializers.ModelSerializer):

    attributes = ProjectAttributeValueEmbeddedSerializer(many=True,
                                                         read_only=True)

    class Meta:
        model = models.Project
        fields = BASIC_PROJECT_FIELDS + (
            'attributes',
        )


class ProjectMeterRunMixin(object):

    def to_representation(self, instance, get_meter_runs=True):

        # get fields in the usual way.
        ret = serializers.Serializer.to_representation(self, instance)

        serializer = MeterRunSummarySerializer(read_only=True)

        if get_meter_runs:
            recent_meter_runs = instance.recent_meter_runs(
                    project_pks=[instance.pk])

            meter_runs = recent_meter_runs[instance.pk]
            _update_with_recent_meter_runs(ret, meter_runs, serializer)

        return ret


class ProjectWithMeterRunsListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        # get fields in the usual way.
        iterable = data.all() if isinstance(data, Manager) else data

        ret = [
            self.child.to_representation(item, get_meter_runs=False)
            for item in iterable
        ]

        project_pks = [p["id"] for p in ret]
        recent_meter_runs = models.Project.recent_meter_runs(
                project_pks=project_pks)

        serializer = MeterRunSummarySerializer(read_only=True)

        for r in ret:
            meter_runs = recent_meter_runs[r["id"]]
            _update_with_recent_meter_runs(r, meter_runs, serializer)

        return ret


class ProjectWithMeterRunsSerializer(ProjectMeterRunMixin,
        serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = BASIC_PROJECT_FIELDS
        list_serializer_class = ProjectWithMeterRunsListSerializer


class ProjectWithAttributesAndMeterRunsSerializer(ProjectMeterRunMixin,
        serializers.ModelSerializer):

    attributes = ProjectAttributeValueEmbeddedSerializer(many=True,
                                                         read_only=True)

    class Meta:
        model = models.Project
        fields = BASIC_PROJECT_FIELDS + (
            'attributes',
        )
        list_serializer_class = ProjectWithMeterRunsListSerializer


class ProjectRunSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectRun
        fields = (
            'id',
            'project',
            'meter_class',
            'meter_settings',
            'status',
            'traceback',
            'added',
            'updated',
        )
        read_only_fields = (
            'status',
            'traceback',
            'added',
            'updated',
        )

    def validate_meter_class(self, value):
        if value not in models.METER_CLASS_CHOICES:
            raise serializers.ValidationError("Invalid meter_class")
        return value
