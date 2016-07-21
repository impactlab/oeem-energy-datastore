from rest_framework import serializers

from .. import models

__all__ = (
    'ProjectSerializer',
    'ProjectWithAttributesSerializer',
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
