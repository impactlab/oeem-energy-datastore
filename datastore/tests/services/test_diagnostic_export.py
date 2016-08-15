from django.test import TestCase
from django.contrib.auth.models import User

from datetime import datetime

import pytz

from datastore.services import create_project, diagnostic_export
from datastore import models
from datastore import tasks


class DiagnosticExportServiceTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            'john', 'lennon@thebeatles.com', 'johnpassword')

        project = create_project(spec={
            "project_id": "CDEF",
            "project_owner": user.projectowner,
            "baseline_period_end": datetime(2012, 1, 1, tzinfo=pytz.UTC),
            "reporting_period_start": datetime(2012, 2, 1, tzinfo=pytz.UTC),
            "zipcode": "91104",
            "traces": [
                {
                    "interpretation": "NG_C_S",
                    "unit": "THM",
                    "start": "2010-01-01",
                    "end": "2014-12-31",
                    "freq": "MS",
                    "value": 1,
                    "nans": set(range(0, 60, 20)),
                    "estimated": set(range(3, 60, 15)),
                },
                {
                    "interpretation": "E_C_S",
                    "unit": "KWH",
                    "start": "2011-01-01",
                    "end": "2014-12-31",
                    "freq": "D",
                    "value": 0.04,
                    "nans": set(range(0, 365*4, 20)),
                    "estimated": set(range(3, 365*4, 15)),
                },
                {
                    "interpretation": "E_OSG_U",
                    "unit": "KWH",
                    "start": "2010-01-01",
                    "end": "2014-12-31",
                    "freq": "D",
                    "value": 0.1,
                    "nans": set(range(0, 365*4, 20)),
                    "estimated": set(range(3, 365*4, 15)),
                },
            ],
        })

        project_run = models.ProjectRun.objects.create(project=project)
        tasks.execute_project_run(project_run.pk)

    def test_basic_usage(self):
        result = diagnostic_export()
        headers = result['headers']
        assert len(headers) == 32

        rows = result['rows']
        assert len(rows) == 1
        row = rows[0]
        assert row['project_id'] == 'CDEF'
        assert 'project_pk' in row
        assert row['project_result_count'] == 1
        assert row['project_run_count'] == 1
        assert row['project_run_count-PENDING'] == 0
        assert row['project_run_count-RUNNING'] == 0
        assert row['project_run_count-SUCCESS'] == 1
        assert row['project_run_count-FAILED'] == 0
        assert row['consumption_metadata_count'] == 3
        assert row['consumption_metadata_count'
                   '-ELECTRICITY_CONSUMPTION_SUPPLIED'] == 1
        assert row['consumption_metadata_count'
                   '-ELECTRICITY_CONSUMPTION_TOTAL'] == 0
        assert row['consumption_metadata_count'
                   '-ELECTRICITY_CONSUMPTION_NET'] == 0
        assert row['consumption_metadata_count'
                   '-ELECTRICITY_ON_SITE_GENERATION_TOTAL'] == 0
        assert row['consumption_metadata_count'
                   '-ELECTRICITY_ON_SITE_GENERATION_CONSUMED'] == 0
        assert row['consumption_metadata_count'
                   '-ELECTRICITY_ON_SITE_GENERATION_UNCONSUMED'] == 1
        assert row['consumption_metadata_count'
                   '-NATURAL_GAS_CONSUMPTION_SUPPLIED'] == 1
