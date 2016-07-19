from .shared import OAuthTestCase
from django.contrib.auth.models import User
from datastore import models
from datetime import datetime, timedelta
import pytz
import json
import numpy as np
from numpy.testing import assert_allclose

class ProjectAPITestCase(OAuthTestCase):

    @classmethod
    def setUpTestData(cls):
        super(ProjectAPITestCase, cls).setUpTestData()

        cls.project = models.Project.objects.create(
            project_owner=cls.user.projectowner,
            project_id="PROJECTID",
            baseline_period_start=None,
            baseline_period_end=datetime(2012, 1, 1, tzinfo=pytz.UTC),
            reporting_period_start=datetime(2012, 1, 2, tzinfo=pytz.UTC),
            reporting_period_end=None,
            zipcode="91104",
            weather_station="722880",
            latitude=0,
            longitude=0,
        )

        cls.cm_ng = models.ConsumptionMetadata.objects.create(
            project=cls.project,
            interpretation="NG_C_S",
            unit="THM",
        )

        cls.cm_e = models.ConsumptionMetadata.objects.create(
            project=cls.project,
            interpretation="E_C_S",
            unit="KWH",
        )

        records = []

        for i in range(0, 700, 30):
            if i % 120 == 0:
                value = np.nan
            else:
                value = 1.0
            records.append(models.ConsumptionRecord(
                metadata=cls.cm_ng,
                start=datetime(2011, 1, 1, tzinfo=pytz.UTC) + timedelta(days=i),
                value=value,
                estimated=False,
            ))

        for i in range(0, 6000):
            if i % 4 == 0:
                value = np.nan
            else:
                value = 1
            records.append(models.ConsumptionRecord(
                metadata=cls.cm_e,
                start=datetime(2011, 12, 1, tzinfo=pytz.UTC) + timedelta(seconds=i*900),
                value=value,
                estimated=False,
            ))

        models.ConsumptionRecord.objects.bulk_create(records)
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
