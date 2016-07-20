from .shared import OAuthTestCase
from django.contrib.auth.models import User

from datetime import datetime, timedelta
import json

import pytz
import numpy as np
from numpy.testing import assert_allclose

from datastore import models
from datastore.services import create_project

class ProjectAPITestCase(OAuthTestCase):

    @classmethod
    def setUpTestData(cls):
        super(ProjectAPITestCase, cls).setUpTestData()

        cls.project = create_project(spec={
            "project_id": "BCDE",
            "project_owner": cls.project_owner,
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
        cls.project.run_meter()

    def test_project_result_read(self):
        response = self.get('/api/v1/project_results/')
        assert response.status_code == 200
        project_result = response.data[0]
        assert list(project_result.keys()) == [
            'id',
            'eemeter_version',
            'meter_class',
            'meter_settings',
            'modeling_periods',
            'modeling_period_groups',
            'derivative_aggregations',
            'energy_trace_model_results',
            'added',
            'updated',
        ]

        modeling_period = project_result['modeling_periods'][0]
        assert list(modeling_period.keys()) == [
            'id',
            'interpretation',
            'start_date',
            'end_date',
        ]

        modeling_period_group = project_result['modeling_period_groups'][0]
        assert list(modeling_period_group.keys()) == [
            'id',
            'baseline_period',
            'reporting_period',
        ]

        derivative_aggregation = project_result['derivative_aggregations'][0]
        assert list(derivative_aggregation.keys()) == [
            'id',
            'modeling_period_group',
            'trace_interpretation',
            'interpretation',
            'baseline_value',
            'baseline_upper',
            'baseline_lower',
            'baseline_n',
            'reporting_value',
            'reporting_upper',
            'reporting_lower',
            'reporting_n',
        ]
        energy_trace_model_result = project_result['energy_trace_model_results'][0]
        assert list(energy_trace_model_result.keys()) == [
            'id',
            'project_result',
            'energy_trace',
            'modeling_period',
            'derivatives',
            'status',
            'r2',
            'rmse',
            'cvrmse',
            'model_serializiation',
            'upper',
            'lower',
            'n',
        ]

        derivative = energy_trace_model_result['derivatives'][0]
        assert list(derivative.keys()) == [
            'id',
            'interpretation',
            'value',
            'upper',
            'lower',
            'n',
        ]
