from rest_framework.permissions import (
    IsAuthenticated,
    DjangoModelPermissionsOrAnonReadOnly,
    BasePermission
)
from rest_framework.decorators import list_route
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import filters
from rest_framework_bulk import BulkModelViewSet
from rest_framework.parsers import BaseParser

import django_filters
from django.db import IntegrityError, transaction
from django.utils.dateparse import parse_datetime

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from . import models
from . import serializers
from . import tasks
from . import services
from collections import defaultdict
from datetime import datetime

from django.conf import settings

if settings.DEBUG:
    default_permissions_classes = [DjangoModelPermissionsOrAnonReadOnly]
else:
    default_permissions_classes = [IsAuthenticated, TokenHasReadWriteScope]

def projects_filter(queryset, value):
    """Project filter for non-project views"""
    return _filter_projects(queryset, value, "project__in")


def _filter_projects(queryset, value, attr):
    """
    Restrict to '+' (http for <space>) separated list of projects.
    """

    project_set = set()
    for part in value.split():
        part_set = _parse_part(part)
        project_set |= part_set

    return queryset.filter(**{attr: project_set})

def _parse_part(part):
    try:
        return set([int(part)])
    except ValueError:
        parts = part.split("-")
        if len(parts) == 2:
            return set(range(int(parts[0]), int(parts[1]) + 1))
        else:
            return set()

class SyncMixin(object):

    @list_route(methods=['post'])
    def sync(self, request):
        self._sync_route_docstring()

        self._create_properties()

        response_data = [self._sync_record(record) for record in request.data]

        # Return a 400 response if any of the records failed to sync
        status_code = 200
        for obj in response_data:
            if "error" in obj.get("status", ""):
                status_code = 400

        return Response(response_data, status=status_code)

    def _sync_record(self, record):
        """ Get/Create/Update records as necessary, returing dict with data
        (as stored in the db) and status.
        If a record is new, add it. If it already exists, decide whether to
        updated it.
        """

        foreign_objects = self._find_foreign_objects(record)
        if "status" in foreign_objects: # one or more not found
            return foreign_objects

        record = self._parse_record(record, foreign_objects)

        try:
            with transaction.atomic():
                obj, created = self._get_or_create(record, foreign_objects)
        except KeyError as e:
            return self._serialize_error(record, "error - missing field", e, foreign_objects)
        except models.Project.MultipleObjectsReturned as e:
            return self._serialize_error(record, "error - multiple records", e, foreign_objects)
        except ValueError as e:
            return self._serialize_error(record, "error - bad field value - create", e, foreign_objects)
        except IntegrityError as e:
            return self._serialize_error(record, "error - integrity error - create", e.__cause__, foreign_objects)

        if created:
            return self._serialize(obj, status="created")

        # (else not created)

        if self._is_different(obj, record):
            if self._should_update(obj, record):
                # update every field
                for attr in self.attributes:
                    setattr(obj, attr, record[attr])

                try:
                    with transaction.atomic():
                        obj.save()
                except ValueError as e:
                    return self._serialize_error(record, "error - bad field value - update", e, foreign_objects)
                except IntegrityError as e:
                    return self._serialize_error(record, "error - integrity error - update", e.__cause__, foreign_objects)

                return self._serialize(obj, status="updated")
            else:
                return self._serialize(obj, status="unchanged - update not valid")
        else:
            return self._serialize(obj, status="unchanged - same record")

    def _is_different(self, existing_obj, new_record_data):
        return any([getattr(existing_obj, attr) != new_record_data[attr]
                    for attr in self.attributes])

    def _should_update(self, existing_obj, new_record_data):
        """ Returns True if existing_project should be updated with
        value and estimated from new_record_data.
        """
        return True

    def _serialize_error(self, record, status, exception, foreign_objects):
        data = self._error_fields(record, foreign_objects)
        data["status"] = status
        data["message"] = str(exception)
        return data


    def _serialize(self, obj, status):
        """ Serialize obj and add sync status
        """
        data = self.sync_serializer_class(obj).data
        data["status"] = status
        return data

    def _get_or_create(self, record, foreign_objects):
        fields = self._get_fields(record, foreign_objects)
        fields["defaults"] = {attr: record[attr] for attr in self.attributes}
        obj, created = self.queryset.get_or_create(**fields)
        return obj, created


class ProjectOwnerViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectOwnerSerializer
    queryset = models.ProjectOwner.objects.all().order_by('pk')


class ConsumptionMetadataFilter(django_filters.FilterSet):

    interpretation = django_filters.MultipleChoiceFilter(
            choices=models.INTERPRETATION_CHOICES)
    unit = django_filters.MultipleChoiceFilter(
            choices=models.UNIT_CHOICES)

    class Meta:
        model = models.ConsumptionMetadata
        fields = ['interpretation', 'unit', 'project']


class ConsumptionMetadataViewSet(SyncMixin, viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ConsumptionMetadata.objects.all().order_by('pk')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ConsumptionMetadataFilter
    sync_serializer_class = serializers.ConsumptionMetadataSummarySerializer

    def get_serializer_class(self):
        if not hasattr(self.request, 'query_params'):
            return serializers.ConsumptionMetadataSerializer

        if self.request.query_params.get("summary", "False") == "True":
            return serializers.ConsumptionMetadataSummarySerializer
        else:
            return serializers.ConsumptionMetadataSerializer

    def _sync_route_docstring(self):
        return """
        `POST /api/v1/consumption_metadatas/sync/`

        Expects records like the following::

            [
                {
                    "project_project_id": "PROJECT_A",
                    "interpretation": "E_C_S",
                    "unit": "KWH"
                },
                ...
            ]

        """

    def _create_properties(self):
        self.attributes = [
            "unit",
        ]

        self.project_dict = {p.project_id: p for p in models.Project.objects.all()}
    def _find_foreign_objects(self, record):

        project = self.project_dict.get(str(record["project_project_id"]))
        if project is None:
            return {
                "status": "error - no Project found",
                "project_project_id": record["project_project_id"],
            }

        return {"project": project}

    def _get_fields(self, record, foreign_objects):
        return {
            "project": foreign_objects["project"],
            "interpretation": record["interpretation"],
        }

    def _error_fields(self, record, foreign_objects):
        return {
            "project": record["project_project_id"],
            "interpretation": record["interpretation"],
        }

    def _parse_record(self, record, foreign_objects):
        return record


class ConsumptionRecordFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter()

    class Meta:
        model = models.ConsumptionRecord
        fields = ['metadata', 'start']


class ConsumptionRecordViewSet(SyncMixin, BulkModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ConsumptionRecord.objects.all().order_by('pk')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ConsumptionRecordFilter
    sync_serializer_class = serializers.ConsumptionRecordSerializer

    def get_serializer_class(self):
        return serializers.ConsumptionRecordSerializer

    def _sync_route_docstring(self):
        return """
        `POST /api/v1/consumption_records/sync/`

        Expects records like the following::

            [
                {
                     "start": "2016-03-15T00:00:00+0000",
                     "end": "2016-03-15T00:15:00+0000",
                     "value": 10.2,
                     "project_id": "SOMEPROJECTID", # not the primary key - the project_id attribute.
                     "interpretation": "ELECTRICITY_CONSUMPTION_SUPPLIED",
                     "unit_name": "KWH"
                },
                ...
            ]

        """


    def _create_properties(self):
        self.attributes = [
            "value",
            "estimated",
        ]

        consumption_metadatas = models.ConsumptionMetadata.objects.all()

        self.metadata_dict = {(cm.project.project_id, cm.interpretation): cm
                         for cm in consumption_metadatas if cm.project}

    def _find_foreign_objects(self, record):

        cm = self.metadata_dict.get((str(record["project_id"]), record["interpretation"]))
        if cm is None:
            return {
                "status": "error - no consumption metadata",
                "start": record["start"],
                "project_id": record["project_id"],
                "interpretation": record["interpretation"],
            }

        return {"metadata": cm}

    def _get_fields(self, record, foreign_objects):
        return {
            "start": record["start"],
            "metadata": foreign_objects["metadata"],
        }

    def _error_fields(self, record, foreign_objects):
        return {
            "start": record["start"],
            "metadata": foreign_objects["metadata"].pk
        }

    def _parse_record(self, record, foreign_objects):
        record["start"] = parse_datetime(record["start"])
        return record

    @list_route(methods=['post'])
    def sync2(self, request):
        """
        `POST /api/v1/consumption_records/sync2/`

        A much faster sync implementation. Slightly different behavior than the existing sync route in that
        it expects a `metadata_id` rather than the metadata properties.

        Expects records like the following::

            [
                {
                     "start": "2016-03-15T00:00:00+0000",
                     "value": 10.2,
                     "metadata_id": 1 # Retrieved using /consumptions_metadata/sync/
                },
                ...
            ]
        """

        fields = ['start', 'value', 'estimated', 'metadata_id']

        records = request.data

        # Wrap as list if missing
        if type(records) is not list:
            records = [records]

        result, status = services.bulk_sync(records, fields, models.ConsumptionRecord, ['start', 'metadata_id'])

        return Response(result, status=status)


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
        return _filter_projects(queryset, value, "pk__in")

class ProjectViewSet(SyncMixin, viewsets.ModelViewSet):

    # parser_classes = (ProjectViewSetParser,)
    permission_classes = default_permissions_classes
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectFilter
    queryset = models.Project.objects.all().order_by('pk')
    sync_serializer_class = serializers.ProjectSerializer

    def get_queryset(self):
        return models.Project.objects.all()\
                                     .prefetch_related('consumptionmetadata_set')\
                                     .prefetch_related('projectattribute_set')\
                                     .prefetch_related('projectattribute_set__key')\
                                     .order_by('pk')


    def get_serializer(self, *args, **kwargs):
        queryset = self.get_queryset()

        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()

        if hasattr(self.request, 'query_params'):

            if self.request.query_params.get('projects'):
                projects = self.request.query_params['projects']
                queryset = _filter_projects(queryset, projects, "pk__in")
                kwargs['context']['project_ids'] = [p.pk for p in queryset]
        else:
            kwargs['context']['project_ids'] = []

        return serializer_class(*args, **kwargs) #data=queryset, context=context, many=True)

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

    def _sync_route_docstring(self):
        return """
        `POST /api/v1/projects/sync/`

        Expects records like the following::

            [
                {
                    "project_id": "ID_1",
                    "project_owner_id": 1,
                    "zipcode": "01234",
                    "weather_station": "012345",
                    "latitude": 89.0,
                    "longitude": -42.0,
                    "baseline_period_end": datetime(2015, 1, 1),
                    "reporting_period_start": datetime(2015, 2, 1),
                },
                ...
            ]

        """


    def _create_properties(self):
        self.attributes = [
            "project_owner_id",
            "zipcode",
            "latitude",
            "longitude",
            "weather_station",
            "baseline_period_end",
            "reporting_period_start",
        ]

    def _find_foreign_objects(self, record):
        return {}

    def _get_fields(self, record, foreign_objects):
        return {
            "project_id": record["project_id"],
        }

    def _error_fields(self, record, foreign_objects):
        return {
            "project_id": record["project_id"],
        }

    def _parse_record(self, record, foreign_objects):

        if record["baseline_period_end"] is not None:
            record["baseline_period_end"] = parse_datetime(record["baseline_period_end"])

        if record["reporting_period_start"] is not None:
            record["reporting_period_start"] = parse_datetime(record["reporting_period_start"])

        return record


class ProjectRunFilter(django_filters.FilterSet):
    projects = django_filters.MethodFilter(action=projects_filter)

    class Meta:
        model = models.ProjectRun
        fields = ['projects']


class ProjectRunViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):

    permission_classes = default_permissions_classes
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectRunFilter

    def perform_create(self, serializer):
      # Create the object normally
      mixins.CreateModelMixin.perform_create(self, serializer)
      project_run = serializer.instance

      # ...and also push a celery job
      tasks.execute_project_run.delay(project_run.pk)

    def get_queryset(self):
        return (models.ProjectRun.objects
                                 .all()
                                 .order_by('pk'))

    def get_serializer_class(self):
        return serializers.ProjectRunSerializer



class MeterRunFilter(django_filters.FilterSet):
    interpretation = django_filters.MultipleChoiceFilter(
            name="consumption_metadata__interpretation",
            choices=models.INTERPRETATION_CHOICES)
    projects = django_filters.MethodFilter(action=projects_filter)
    most_recent = django_filters.MethodFilter(action="most_recent_filter")

    class Meta:
        model = models.MeterRun
        fields = ['interpretation', 'most_recent', 'projects']

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
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MeterRunFilter

    def get_queryset(self):
        return models.MeterRun.objects.all()\
                                     .prefetch_related('consumption_metadata')\
                                     .order_by('pk')

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


class ProjectAttributeKeyViewSet(SyncMixin, viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectAttributeKeySerializer
    queryset = models.ProjectAttributeKey.objects.all().order_by('pk')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectAttributeKeyFilter
    sync_serializer_class = serializers.ProjectAttributeKeySerializer

    def _sync_route_docstring(self):
        return """
        `POST /api/v1/project_attribute_keys/sync/`

        Expects records like the following::

            [
                {
                    "name": "project_cost",
                    "display_name": "Project Cost",
                    "data_type": 100.0,
                },
                ...
            ]

        """

    def _create_properties(self):
        self.attributes = [
            "display_name",
            "data_type",
        ]

    def _find_foreign_objects(self, record):
        return {}

    def _get_fields(self, record, foreign_objects):
        return {
            "name": record["name"],
        }

    def _error_fields(self, record, foreign_objects):
        return {
            "name": record["name"],
        }

    def _parse_record(self, record, foreign_objects):
        return record


class ProjectAttributeFilter(django_filters.FilterSet):

    class Meta:
        model = models.ProjectAttribute
        fields = ['key', 'project']


class ProjectAttributeViewSet(SyncMixin, viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ProjectAttribute.objects.all().order_by('pk')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectAttributeFilter
    sync_serializer_class = serializers.ProjectAttributeValueSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.ProjectAttributeValueSerializer
        else:
            return serializers.ProjectAttributeSerializer

    def _sync_route_docstring(self):
        return """
        `POST /api/v1/project_attributes/sync/`

        Expects records like the following::

            [
                {
                    "project_project_id": "ID_1",
                    "project_attribute_key_name": "project_cost",
                    "value": 100.0,
                },
                ...
            ]

        """

    def _create_properties(self):

        self.attributes = [
            "boolean_value",
            "char_value",
            "date_value",
            "datetime_value",
            "float_value",
            "integer_value",
        ]

        self.project_dict = {p.project_id: p for p in models.Project.objects.all()}
        self.project_attribute_key_dict = {pak.name: pak for pak in models.ProjectAttributeKey.objects.all()}

    def _find_foreign_objects(self, record):

        project = self.project_dict.get(record["project_project_id"])
        if project is None:
            return {
                "status": "error - no Project found",
                "project_project_id": record["project_project_id"],
            }

        key = self.project_attribute_key_dict.get(record["project_attribute_key_name"])
        if key is None:
            return {
                "status": "error - no ProjectAttributeKey found",
                "project_attribute_key_name": record["project_attribute_key_name"],
            }

        return {"key": key, "project": project}

    def _get_fields(self, record, foreign_objects):
        return {
            "project": foreign_objects["project"],
            "key": foreign_objects["key"],
        }

    def _error_fields(self, record, foreign_objects):
        return {
            "project_project_id": record["project_project_id"],
            "project_attribute_key_name": record["project_attribute_key_name"],
        }

    def _parse_record(self, record, foreign_objects):
        key = foreign_objects["key"]
        value = record.pop("value")
        record["boolean_value"] = None
        record["char_value"] = None
        record["date_value"] = None
        record["datetime_value"] = None
        record["float_value"] = None
        record["integer_value"] = None
        if key.data_type == "BOOLEAN":
            record["boolean_value"] = value
        elif key.data_type == "CHAR":
            record["char_value"] = value
        elif key.data_type == "DATE":
            record["date_value"] = value
        elif key.data_type == "DATETIME":
            record["datetime_value"] = value
        elif key.data_type == "FLOAT":
            record["float_value"] = value
        elif key.data_type == "INTEGER":
            record["integer_value"] = value
        return record
