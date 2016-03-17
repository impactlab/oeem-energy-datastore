from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework_bulk import BulkModelViewSet
from rest_framework.parsers import JSONParser
from django.utils.six import BytesIO

import django_filters

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from . import models
from . import serializers
from collections import defaultdict
from datetime import datetime

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

    class Meta:
        model = models.ConsumptionMetadata
        fields = ['fuel_type', 'energy_unit', 'project']


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

    @list_route(methods=['post'])
    def sync(self, request):
        """
        `POST /api/v1/consumption_records/sync/`

        Expects records like the following::

            [
                {
                     "start": "2016-03-15T00:00:00+0000",
                     "end": "2016-03-15T00:15:00+0000",
                     "value": 10.2,
                     "project_id": "SOMEPROJECTID", # not the primary key - the project_id attribute.
                     "fuel_type": "electricity",
                     "unit_name": "kWh"
                },
                ...
            ]

        """

        consumption_metadatas = models.ConsumptionMetadata.objects.all()
        self.metadata_dict = {(cm.project.project_id, cm.fuel_type): cm
                         for cm in consumption_metadatas}

        response_data = [self._sync_record(record) for record in request.data]

        return Response(response_data)

    def _sync_record(self, record):
        """ Get/Create/Update records as necessary, returing dict with data
        (as stored in the db) and status.
        If a record is new, add it. If it already exists, decide whether to
        updated it.
        """

        record = self._parse_record(record)

        cm = self.metadata_dict.get((record["project_id"], record["fuel_type"]))
        if cm is None:
            return {
                "status": "error - no consumption metadata",
                "start": record["start"],
                "project_id": record["project_id"],
                "fuel_type": record["fuel_type"],
            }


        try:
            # assume metadata and start uniquely identify record.
            # other fields might change and need to be updated.
            consumption_record, created = self.queryset.get_or_create(
                    metadata=cm,
                    start=record["start"],
                    defaults={
                        "value": record["value"],
                        "estimated": record["estimated"]
                    })

        except models.ConsumptionRecord.MultipleObjectsReturned:
            return {
                "status": "error - multiple records",
                "start": record["start"],
                "metadata": cm.pk
            }

        if created:
            return self._serialize(consumption_record, status="created")

        if self._is_different(consumption_record, record):
            if self._should_update(consumption_record, record):
                consumption_record.value = record["value"]
                consumption_record.estimated = record["estimated"]
                consumption_record.save()

                return self._serialize(consumption_record, status="updated")
            else:
                return self._serialize(consumption_record, status="unchanged - update not valid")
        else:
            return self._serialize(consumption_record, status="unchanged - same record")

    def _serialize(self, consumption_record, status):
        """ Serialize consumption record and add sync status
        """
        data = self.get_serializer_class()(consumption_record).data
        data["status"] = status
        return data

    def _is_different(self, existing_consumption_record, new_record_data):
        value_different = existing_consumption_record.value != new_record_data["value"]
        estimated_different = existing_consumption_record.estimated != new_record_data["estimated"]
        return value_different or estimated_different

    def _should_update(self, existing_consumption_record, new_record_data):
        """ Returns True if existing_consumption_record should be updated with
        value and estimated from new_record_data.
        """
        return True

    def _parse_record(self, record):
        record["start"] = datetime.strptime(record["start"], "%Y-%m-%dT%H:%M:%S%z")
        return record

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
