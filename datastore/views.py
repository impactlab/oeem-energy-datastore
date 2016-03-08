from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework_bulk import BulkModelViewSet

import django_filters

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from . import models
from . import serializers
from collections import defaultdict

default_permissions_classes = [IsAuthenticated, TokenHasReadWriteScope]


def projects_filter(queryset, value):
    """
    Restrict to '+' (http for <space>) separated list of projects.
    """
    try:
        project_set = set(int(p) for p in value.split())
    except ValueError:
        project_set = set()
    return queryset.filter(project__in=project_set)


class ProjectOwnerViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectOwnerSerializer
    queryset = models.ProjectOwner.objects.all().order_by('pk')


class ConsumptionMetadataFilter(django_filters.FilterSet):

    fuel_type = django_filters.MultipleChoiceFilter(
            choices=models.FUEL_TYPE_CHOICES)
    energy_unit = django_filters.MultipleChoiceFilter(
            choices=models.ENERGY_UNIT_CHOICES)
    projects = django_filters.MethodFilter(
            action=projects_filter)

    class Meta:
        model = models.ConsumptionMetadata
        fields = ['fuel_type', 'energy_unit', 'projects']


class ConsumptionMetadataViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ConsumptionMetadata.objects.all().order_by('pk')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ConsumptionMetadataFilter

    def get_serializer_class(self):
        if not hasattr(self.request, 'query_params'):
            return serializers.ConsumptionMetadataSerializer

        if self.request.query_params.get("summary", "False") == "True":
            return serializers.ConsumptionMetadataSummarySerializer
        else:
            return serializers.ConsumptionMetadataSerializer


class ConsumptionRecordFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter()

    class Meta:
        model = models.ConsumptionRecord
        fields = ['metadata', 'start']


class ConsumptionRecordViewSet(BulkModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ConsumptionRecord.objects.all().order_by('pk')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ConsumptionRecordFilter

    def get_serializer_class(self):
        return serializers.ConsumptionRecordSerializer


class ProjectFilter(django_filters.FilterSet):

    projectblock_and = django_filters.ModelMultipleChoiceFilter(
            name='projectblock',
            queryset=models.ProjectBlock.objects.all(),
            conjoined=True)
    projectblock_or = django_filters.ModelMultipleChoiceFilter(
            name='projectblock',
            queryset=models.ProjectBlock.objects.all(),
            conjoined=False)
    projects = django_filters.MethodFilter(
            action="projects_filter")
    baseline_period_end = django_filters.DateFromToRangeFilter()
    reporting_period_start = django_filters.DateFromToRangeFilter()

    class Meta:
        model = models.Project
        fields = [
            'zipcode',
            'projectblock_and',
            'projectblock_or',
            'projects',
            'project_id',
            'weather_station',
            'project_owner',
            'baseline_period_end',
            'reporting_period_start',
        ]

    def projects_filter(self, queryset, value):
        """
        Restrict to '+' (http for <space>) separated list of projects.
        """
        try:
            project_set = set(int(p) for p in value.split())
        except ValueError:
            project_set = set()
        return queryset.filter(pk__in=project_set)


class ProjectViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectFilter
    queryset = models.Project.objects.all().order_by('pk')

    def get_serializer_class(self):
        if not hasattr(self.request, 'query_params'):
            return serializers.ProjectSerializer

        if self.request.query_params.get(
                "with_monthly_summary", "False") == "True":
            return serializers.ProjectWithMonthlyMeterRunsSerializer

        with_attributes = self.request.query_params.get(
                "with_attributes", "False") == "True"
        with_meter_runs = self.request.query_params.get(
                "with_meter_runs", "False") == "True"

        if with_attributes:
            if with_meter_runs:
                return serializers.ProjectWithAttributesAndMeterRunsSerializer
            else:
                return serializers.ProjectWithAttributesSerializer
        else:
            if with_meter_runs:
                return serializers.ProjectWithMeterRunsSerializer
            else:
                return serializers.ProjectSerializer


class MeterRunFilter(django_filters.FilterSet):
    fuel_type = django_filters.MultipleChoiceFilter(
            name="consumption_metadata__fuel_type",
            choices=models.FUEL_TYPE_CHOICES)
    projects = django_filters.MethodFilter(action=projects_filter)
    most_recent = django_filters.MethodFilter(action="most_recent_filter")

    class Meta:
        model = models.MeterRun
        fields = ['fuel_type', 'most_recent', 'projects']

    def most_recent_filter(self, queryset, value):
        if value != "True":
            return queryset

        encountered_cms = set()
        accepted_meter_runs = set()
        for meter_run in queryset.order_by('-updated').all():
            if meter_run.consumption_metadata not in encountered_cms:
                encountered_cms.add(meter_run.consumption_metadata)
                accepted_meter_runs.add(meter_run.pk)

        return queryset.filter(pk__in=accepted_meter_runs)


class MeterRunViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.MeterRun.objects.all().order_by('pk')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MeterRunFilter

    def get_serializer_class(self):
        if not hasattr(self.request, 'query_params'):
            return serializers.MeterRunSerializer

        if self.request.query_params.get("summary", "False") == "True":
            return serializers.MeterRunSummarySerializer
        elif self.request.query_params.get("daily", "False") == "True":
            return serializers.MeterRunDailySerializer
        elif self.request.query_params.get("monthly", "False") == "True":
            return serializers.MeterRunMonthlySerializer
        else:
            return serializers.MeterRunSerializer


class ProjectBlockViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ProjectBlock.objects.all().order_by('pk')

    def get_serializer_class(self):
        if not hasattr(self.request, 'query_params'):
            return serializers.ProjectBlockSerializer

        if self.request.query_params.get("monthly_timeseries", "false") == "True":
            return serializers.ProjectBlockMonthlyTimeseriesSerializer

        if self.request.query_params.get("name_only", "false") == "True":
            return serializers.ProjectBlockNameSerializer
        else:
            return serializers.ProjectBlockSerializer


class ProjectAttributeKeyFilter(django_filters.FilterSet):

    class Meta:
        model = models.ProjectAttributeKey
        fields = ['name', 'data_type']


class ProjectAttributeKeyViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectAttributeKeySerializer
    queryset = models.ProjectAttributeKey.objects.all().order_by('pk')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectAttributeKeyFilter


class ProjectAttributeFilter(django_filters.FilterSet):

    class Meta:
        model = models.ProjectAttribute
        fields = ['key', 'project']


class ProjectAttributeViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ProjectAttribute.objects.all().order_by('pk')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectAttributeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.ProjectAttributeValueSerializer
        else:
            return serializers.ProjectAttributeSerializer
