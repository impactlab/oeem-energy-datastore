from rest_framework import serializers

from .. import models

from .projects import (
    ProjectSerializer,
    ProjectWithAttributesSerializer,
    ProjectRunSerializer,
)

from .project_results import (
    ProjectResultSerializer,
)

__all__ = (
    'ProjectSerializer',
    'ProjectWithAttributesSerializer',
    'ProjectRunSerializer',
    'ProjectResultSerializer',
    'ProjectOwnerSerializer',
    'ProjectBlockSerializer',
    'ProjectBlockNameSerializer',
    'ProjectAttributeKeySerializer',
    'ProjectAttributeSerializer',
    'ProjectAttributeValueSerializer',
    'ConsumptionRecordSerializer',
    'ConsumptionMetadataSummarySerializer',
    'ConsumptionRecordEmbeddedSerializer',
    'ConsumptionMetadataSerializer',
)


class ProjectOwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectOwner
        fields = (
            'id',
            'user'
        )


class ProjectBlockSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectBlock
        fields = (
            'id',
            'name',
            'projects'
        )


class ProjectBlockNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectBlock
        fields = (
            'id',
            'name'
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


class ConsumptionRecordSerializer(serializers.ModelSerializer):

    value = serializers.FloatField(source='value_clean')

    class Meta:
        model = models.ConsumptionRecord
        fields = (
            'id',
            'start',
            'value',
            'estimated',
            'metadata',
        )

    def create(self, validated_data):
        value_clean = validated_data.pop('value_clean')
        validated_data["value"] = value_clean
        return models.ConsumptionRecord.objects.create(**validated_data)


class ConsumptionMetadataSummarySerializer(serializers.ModelSerializer):

    project = ProjectSerializer(required=False)

    class Meta:
        model = models.ConsumptionMetadata
        fields = (
            'id',
            'interpretation',
            'unit',
            'project',
            'label',
        )


class ConsumptionRecordEmbeddedSerializer(serializers.ModelSerializer):

    value = serializers.FloatField(source='value_clean')

    class Meta:
        model = models.ConsumptionRecord
        fields = (
            'id',
            'start',
            'value',
            'estimated',
        )


class ConsumptionMetadataSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ConsumptionMetadata
        fields = (
            'id',
            'interpretation',
            'unit',
            'project',
            'label',
        )





