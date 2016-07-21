from django.test import TestCase
from django.contrib.auth.models import User

from datetime import datetime

import pytz

from datastore.services import create_project, projectresult_export


class ExportServiceTestCase(TestCase):

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
                    "interpretation": "NG_C_S",
                    "unit": "THM",
                    "start": "2011-09-01",
                    "end": "2014-12-31",
                    "freq": "D",
                    "value": 2,
                    "nans": set(range(0, 1000, 20)),
                    "estimated": set(range(3, 1000, 15)),
                },
                {
                    "interpretation": "E_C_S",
                    "unit": "KWH",
                    "start": "2011-01-01",
                    "end": "2014-12-31",
                    "freq": "15T",
                    "value": 0.04,
                    "nans": set(range(0, 96*365*4, 200)),
                    "estimated": set(range(3, 96*365*4, 150)),
                },
                {
                    "interpretation": "E_C_S",
                    "unit": "KWH",
                    "start": "2011-01-01",
                    "end": "2014-12-31",
                    "freq": "H",
                    "value": 0.4,
                    "nans": set(range(0, 96*365*4, 200)),
                    "estimated": set(range(3, 96*365*4, 150)),
                },
                {
                    "interpretation": "E_OSG_U",
                    "unit": "KWH",
                    "start": "2012-01-15",
                    "end": "2014-12-31",
                    "freq": "H",
                    "value": 0.3,
                    "nans": set(range(0, 96*365*4, 200)),
                    "estimated": set(range(3, 96*365*4, 150)),
                },
                {
                    "interpretation": "E_OSG_U",
                    "unit": "KWH",
                    "start": "2010-01-01",
                    "end": "2014-12-31",
                    "freq": "30T",
                    "value": 0.1,
                    "nans": set(range(0, 96*365*4, 200)),
                    "estimated": set(range(3, 96*365*4, 150)),
                },
            ],
        })
        project.run_meter()

    def test_export(self):
        result = projectresult_export()
        headers = result['headers']
        assert len(headers) == 87
        project_results = result['project_results']
        assert len(project_results) == 1
