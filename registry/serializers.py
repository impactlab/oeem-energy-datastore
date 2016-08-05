from rest_framework import serializers

from registry import models


class ConnectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Connection
        fields = (
            'id',
            'projects',
            'token',
        )

    def create(self, validated_data):
        projects = self.initial_data.pop('projects', [])
        connection = models.Connection.objects.create(**validated_data)
        models.ConnectionMembership.objects.bulk_create([
            models.ConnectionMembership(project_id=project_id,
                                        connection=connection)
            for project_id in projects
        ])
        return connection
