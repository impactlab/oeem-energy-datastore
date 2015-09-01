from .models import Project
from .models import ConsumptionMetadata
from .serializers import ProjectSerializer
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
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
