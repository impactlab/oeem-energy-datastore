from rest_framework import generics, permissions
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from . import models
from . import serializers

##### Consumption

class ConsumptionMetadataList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.ConsumptionMetadata.objects.all()
    serializer_class = serializers.ConsumptionMetadataSerializer

class ConsumptionMetadataDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.ConsumptionMetadata.objects.all()
    serializer_class = serializers.ConsumptionMetadataSerializer


##### Projects

class ProjectList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
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

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer

##### Meter Runs

class MeterRunList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.MeterRun.objects.all()
    serializer_class = serializers.MeterRunSerializer

class MeterRunDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.MeterRun.objects.all()
    serializer_class = serializers.MeterRunSerializer

class MeterRunSummaryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.MeterRun.objects.all()
    serializer_class = serializers.MeterRunSummarySerializer

class MeterRunDailyDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.MeterRun.objects.all()
    serializer_class = serializers.MeterRunDailySerializer

class MeterRunMonthlyDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.MeterRun.objects.all()
    serializer_class = serializers.MeterRunMonthlySerializer


##### Project Blocks

class ProjectBlockList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.ProjectBlock.objects.all()
    serializer_class = serializers.ProjectBlockSerializer

class ProjectBlockDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.ProjectBlock.objects.all()
    serializer_class = serializers.ProjectBlockSerializer

class ProjectBlockMonthlyTimeseriesDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = models.ProjectBlock.objects.all()
    serializer_class = serializers.ProjectBlockMonthlyTimeseriesSerializer
