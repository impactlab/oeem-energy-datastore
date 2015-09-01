from datastore.models import ConsumptionMetadata
from datastore.serializers import ConsumptionMetadataSerializer

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
