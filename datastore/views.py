from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework import viewsets

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from . import models
from . import serializers

default_permissions_classes = [IsAuthenticated, TokenHasReadWriteScope]

class ConsumptionMetadataViewSet(viewsets.ModelViewSet):
    permission_classes = default_permissions_classes
    queryset = models.ConsumptionMetadata.objects.all()
    serializer_class = serializers.ConsumptionMetadataSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = models.Project.objects.all()
        project_block_id = self.request.query_params.get('project_block', None)
        if project_block_id is not None:
            queryset = queryset.filter(projectblock=project_block_id)
        return queryset


class MeterRunViewSet(viewsets.ModelViewSet):
    permission_classes = default_permissions_classes
    serializer_class = serializers.MeterRunSerializer
    queryset = models.MeterRun.objects.all()

    @list_route()
    def summary(self, request):
        queryset = self.get_queryset()
        serializer = serializers.MeterRunSummarySerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route()
    def daily(self, request):
        queryset = self.get_queryset()
        serializer = serializers.MeterRunDailySerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route()
    def monthly(self, request):
        queryset = self.get_queryset()
        serializer = serializers.MeterRunMonthlySerializer(queryset, many=True)
        return Response(serializer.data)


class ProjectBlockViewSet(viewsets.ModelViewSet):
    permission_classes = default_permissions_classes
    serializer_class = serializers.ProjectBlockSerializer
    queryset = models.ProjectBlock.objects.all()

    @list_route()
    def monthly_timeseries(self, request):
        queryset = self.get_queryset()
        serializer = serializers.ProjectBlockMonthlyTimeseriesSerializer(queryset, many=True)
        return Response(serializer.data)
