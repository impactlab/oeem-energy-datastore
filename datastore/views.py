from .models import Project
from .models import MeterRun
from .models import ProjectBlock
from .models import ConsumptionMetadata
from .serializers import ProjectSerializer
from .serializers import MeterRunSerializer
from .serializers import ProjectBlockSerializer
from .serializers import ConsumptionMetadataSerializer

from rest_framework import generics, permissions
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

class ConsumptionMetadataList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = ConsumptionMetadata.objects.all()
    serializer_class = ConsumptionMetadataSerializer

class ConsumptionMetadataDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = ConsumptionMetadata.objects.all()
    serializer_class = ConsumptionMetadataSerializer

class ProjectList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Project.objects.all()
        project_block_id = self.request.query_params.get('project_block', None)
        if project_block_id is not None:
            queryset = queryset.filter(projectblock=project_block_id)
        return queryset

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class MeterRunList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = MeterRun.objects.all()
    serializer_class = MeterRunSerializer

class MeterRunDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = MeterRun.objects.all()
    serializer_class = MeterRunSerializer

class ProjectBlockList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = ProjectBlock.objects.all()
    serializer_class = ProjectBlockSerializer

class ProjectBlockDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = ProjectBlock.objects.all()
    serializer_class = ProjectBlockSerializer

