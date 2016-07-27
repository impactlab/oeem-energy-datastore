from django.test import Client, TestCase
from django.contrib.auth.models import User

import uuid
from datetime import datetime

import pytz

from registry.models import Connection, ConnectionMembership
from datastore.services import create_project


class RegistrySummaryViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com',
                                             'johnpassword')

        self.project = create_project(spec={
            "project_id": uuid.uuid4(),
            "project_owner": self.user.projectowner,
            "baseline_period_end": datetime(2012, 1, 1, tzinfo=pytz.UTC),
            "reporting_period_start": datetime(2012, 2, 1, tzinfo=pytz.UTC),
            "zipcode": "91104",
            "traces": [
                {
                    "interpretation": "E_C_S",
                    "unit": "KWH",
                    "start": "2010-01-01",
                    "end": "2014-12-31",
                    "freq": "MS",
                    "value": 1,
                    "nans": set(range(0, 60, 20)),
                    "estimated": set(range(3, 60, 15)),
                },
            ],
        })
        self.project.run_meter()

        self.connection = Connection.create(projects=[self.project])

        self.client = Client()

    def test_basic(self):
        token = self.connection.token
        response = self.client.get(
            '/registry/summary/', HTTP_AUTHORIZATION='Token {}'.format(token))

        data = response.json()
        projects = data['projects']
        assert len(projects) == 1
        project = projects[0]
        assert len(project['registry_id']) == 36
        assert project['meter_class'] == 'EnergyEfficiencyMeter'
        assert project['meter_settings'] is None
        assert 'eemeter_version' in project
        summaries = project['summaries']
        assert len(summaries) == 4
        summary = summaries[0]
        assert 'baseline_value' in summary
        assert 'baseline_upper' in summary
        assert 'baseline_lower' in summary
        assert 'reporting_value' in summary
        assert 'reporting_upper' in summary
        assert 'reporting_lower' in summary
        assert 'derivative_interpretation' in summary
        assert 'trace_interpretation' in summary
