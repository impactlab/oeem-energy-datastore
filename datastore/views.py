from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework import viewsets
from rest_framework.response import Response

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from . import models
from . import serializers

default_permissions_classes = [IsAuthenticated, TokenHasReadWriteScope]

class ProjectOwnerViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectOwnerSerializer
    queryset = models.ProjectOwner.objects


class ConsumptionMetadataViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ConsumptionMetadataSerializer
    queryset = models.ConsumptionMetadata.objects


class ProjectViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = models.Project.objects
        project_block_id = self.request.query_params.get('project_block', None)
        if project_block_id is not None:
            queryset = queryset.filter(projectblock=project_block_id)
        return queryset


class MeterRunViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.MeterRun.objects

    def get_serializer_class(self):
        if self.request.query_params.get("summary", "false") == "true":
            return serializers.MeterRunSummarySerializer
        elif self.request.query_params.get("daily", "false") == "true":
            return serializers.MeterRunDailySerializer
        elif self.request.query_params.get("monthly", "false") == "true":
            return serializers.MeterRunMonthlySerializer
        else:
            return serializers.MeterRunSerializer


class ProjectBlockViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ProjectBlock.objects

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
    queryset = models.ProjectAttributeKey.objects


class ProjectAttributeViewSet(viewsets.ModelViewSet):

    permission_classes = default_permissions_classes
    queryset = models.ProjectAttribute.objects

    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.ProjectAttributeValueSerializer
        else:
            return serializers.ProjectAttributeSerializer
