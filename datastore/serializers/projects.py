from rest_framework import serializers

from django.db.models import Manager

from .meter_runs import (
    MeterRunSummarySerializer,
    MeterRunMonthlySerializer,
)

from .. import models

__all__ = (
    'ProjectSerializer',
    'ProjectWithAttributesSerializer',
    'ProjectWithMeterRunsSerializer',
    'ProjectWithMonthlyMeterRunsSerializer',
    'ProjectWithAttributesAndMeterRunsSerializer',
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
        meter_run.update({"fuel_type": v["fuel_type"]})
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

    include_monthly = False

    def to_representation(self, instance, get_meter_runs=True):

        # get fields in the usual way.
        ret = serializers.Serializer.to_representation(self, instance)

        if self.include_monthly:
            serializer = MeterRunMonthlySerializer(read_only=True)
        else:
            serializer = MeterRunSummarySerializer(read_only=True)

        if get_meter_runs:
            recent_meter_runs = instance.recent_meter_runs(
                    project_pks=[instance.pk])

            meter_runs = recent_meter_runs[instance.pk]
            _update_with_recent_meter_runs(ret, meter_runs, serializer)

        return ret

class ProjectMeterRunMonthlyMixin(ProjectMeterRunMixin):
    include_monthly = True


class ProjectWithMeterRunsListSerializer(serializers.ListSerializer):

    include_monthly = False

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

        if self.include_monthly:
            serializer = MeterRunMonthlySerializer(read_only=True)
        else:
            serializer = MeterRunSummarySerializer(read_only=True)

        for r in ret:
            meter_runs = recent_meter_runs[r["id"]]
            _update_with_recent_meter_runs(r, meter_runs, serializer)

        return ret


class ProjectWithMeterRunsMonthlyListSerializer(
        ProjectWithMeterRunsListSerializer):
    include_monthly = True


class ProjectWithMeterRunsSerializer(ProjectMeterRunMixin,
        serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = BASIC_PROJECT_FIELDS
        list_serializer_class = ProjectWithMeterRunsListSerializer


class ProjectWithMonthlyMeterRunsSerializer(ProjectMeterRunMonthlyMixin,
        serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = BASIC_PROJECT_FIELDS
        list_serializer_class = ProjectWithMeterRunsMonthlyListSerializer


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
