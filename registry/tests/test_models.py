from django.test import TestCase
from django.contrib.auth.models import User

import uuid
from datetime import datetime

import pytz

from registry.models import Connection, ConnectionMembership
from datastore.services import create_project


class ConnectionTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com',
                                             'johnpassword')

        self.project = create_project(spec={
            "project_id": uuid.uuid4(),
            "project_owner": self.user.projectowner,
            "baseline_period_end": datetime(2012, 1, 1, tzinfo=pytz.UTC),
            "reporting_period_start": datetime(2012, 2, 1, tzinfo=pytz.UTC),
            "zipcode": "91104",
            "traces": [],
        })

    def test_empty(self):
        connection = Connection.objects.create()
        assert len(str(connection.token)) == 36
        assert connection.projects.count() == 0

    def test_basic_create(self):
        connection = Connection.objects.create()
        ConnectionMembership.objects.create(project=self.project,
                                            connection=connection)
        assert connection.projects.count() == 1
        membership = connection.connectionmembership_set \
            .get(project=self.project)
        assert len(str(membership.registry_id)) == 36

    def test_factory_create(self):
        connection = Connection.create(projects=[self.project])
        assert connection.projects.count() == 1
