from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import uuid
from collections import OrderedDict

from datastore import models as datastore_models
from oeem_energy_datastore import VERSION



@python_2_unicode_compatible
class Connection(models.Model):
    projects = models.ManyToManyField(datastore_models.Project,
                                      through='ConnectionMembership')

    token = models.UUIDField(default=uuid.uuid4, db_index=True)

    def __str__(self):
        return (
            u'Connection(projects={}, token={})'
            .format(self.projects, self.token)
        )

    @classmethod
    def create(cls, projects):
        connection = cls.objects.create()
        ConnectionMembership.objects.bulk_create([
            ConnectionMembership(project=project, connection=connection)
            for project in projects
        ])
        return connection

    def summary_data(self):
        connection_memberships = self.connectionmembership_set.all() \
            .prefetch_related(
                'project',
                'project__project_results',
                'project__project_results__derivative_aggregations'
            ).order_by('-pk')

        projects = []
        for membership in connection_memberships:

            project_results = membership.project.project_results\
                .order_by('-pk')
            if len(project_results) == 0:
                continue
            project_result = project_results[0]

            summaries = [
                OrderedDict([
                    ("trace_interpretation", agg.trace_interpretation),
                    ("derivative_interpretation", agg.interpretation),
                    ("baseline_value", agg.baseline_value),
                    ("baseline_upper", agg.baseline_upper),
                    ("baseline_lower", agg.baseline_lower),
                    ("reporting_value", agg.reporting_value),
                    ("reporting_upper", agg.reporting_upper),
                    ("reporting_lower", agg.reporting_lower),
                ])
                for agg in project_result.derivative_aggregations.all()
            ]
            project_data = OrderedDict([
                ("registry_id", membership.registry_id),
                ("eemeter_version", project_result.eemeter_version),
                ("meter_class", project_result.meter_class),
                ("meter_settings", project_result.meter_settings),
                ("summaries", summaries),
            ])
            projects.append(project_data)

        return OrderedDict([
            ("datastore_version", VERSION),
            ("projects", projects),
        ])


@python_2_unicode_compatible
class ConnectionMembership(models.Model):
    registry_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                   editable=False)
    project = models.ForeignKey(datastore_models.Project,
                                on_delete=models.CASCADE)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE)

    def __str__(self):
        return (
            u'ConnectionMembership(registry_id={}, project={}, connection={})'
            .format(self.registry_id, self.project, self.connection)
        )
