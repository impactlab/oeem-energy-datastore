from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
import django_filters

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from . import models
from . import serializers

default_permissions_classes = [IsAuthenticated, TokenHasReadWriteScope]

class ProjectOwnerViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectOwnerSerializer
    queryset = models.ProjectOwner.objects.all()


class ConsumptionMetadataViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ConsumptionMetadataSerializer
    queryset = models.ConsumptionMetadata.objects.all()


class ProjectFilter(django_filters.FilterSet):

    projectblock_and = django_filters.ModelMultipleChoiceFilter(
            name='projectblock',
            queryset=models.ProjectBlock.objects.all(),
            conjoined=True)
    projectblock_or = django_filters.ModelMultipleChoiceFilter(
            name='projectblock',
            queryset=models.ProjectBlock.objects.all(),
            conjoined=False)

    class Meta:
        model = models.Project
        fields = ['zipcode', 'projectblock_and', 'projectblock_or']


class ProjectViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectFilter
    queryset = models.Project.objects.all()


class MeterRunViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.MeterRun.objects.all()

    def get_serializer_class(self):
        if self.request.query_params.get("summary", "false") == "true":
            return serializers.MeterRunSummarySerializer
        elif self.request.query_params.get("daily", "false") == "true":
            return serializers.MeterRunDailySerializer
        elif self.request.query_params.get("monthly", "false") == "true":
            return serializers.MeterRunMonthlySerializer
        else:
            return serializers.MeterRunSerializer


class RecentMeterRunViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.MeterRunSummarySerializer

    def get_queryset(self):
        queryset = models.MeterRun.objects.all()

        projects = self.request.query_params.get("projects")
        if projects is None:
            project_list = []
        else:
            project_list = [int(p) for p in projects.split()]
        queryset = queryset.filter(project__in=project_list)

        return queryset


class ProjectBlockViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ProjectBlock.objects.all()

    def get_serializer_class(self):
        if self.request.query_params.get("monthly_timeseries", "false") == "true":
            return serializers.ProjectBlockMonthlyTimeseriesSerializer
        if self.request.query_params.get("name_only", "false") == "true":
            return serializers.ProjectBlockNameSerializer
        else:
            return serializers.ProjectBlockSerializer


class ProjectAttributeKeyViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectAttributeKeySerializer
    queryset = models.ProjectAttributeKey.objects.all()


class ProjectAttributeViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ProjectAttribute.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.ProjectAttributeValueSerializer
        else:
            return serializers.ProjectAttributeSerializer
