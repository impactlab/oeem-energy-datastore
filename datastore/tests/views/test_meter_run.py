from django.utils.timezone import now, timedelta, make_aware
from datastore import models
from .shared import OAuthTestCase

from oauth2_provider.models import AccessToken

from eemeter.consumption import ConsumptionData as EEMeterConsumptionData
from eemeter.project import Project as EEMeterProject
from eemeter.examples import get_example_project
from eemeter.evaluation import Period

from datetime import datetime

import json
import pytz
from six import string_types

class MeterRunAPITestCase(OAuthTestCase):

    @classmethod
    def setUpTestData(cls):

        super(MeterRunAPITestCase, cls).setUpTestData()

        cls.project = models.Project.objects.create(
            project_owner=cls.user.projectowner,
            project_id="PROJECT_ID",
            baseline_period_start=None,
            baseline_period_end=datetime(2012, 1, 1, tzinfo=pytz.UTC),
            reporting_period_start=datetime(2012, 2, 1, tzinfo=pytz.UTC),
            reporting_period_end=None,
            zipcode="91104",
            weather_station="722880",
            latitude=0,
            longitude=0,
        )

        elec = models.ConsumptionMetadata.objects.create(
            project=cls.project,
            fuel_type="E",
            energy_unit="KWH",
        )

        gas = models.ConsumptionMetadata.objects.create(
            project=cls.project,
            fuel_type="NG",
            energy_unit="THM",
        )

        cls.consumption_metadatas = [elec, gas]

        for i in range(0, 1000, 30):
            models.ConsumptionRecord.objects.create(
                metadata=elec,
                start=datetime(2011, 1, 1, tzinfo=pytz.UTC) + timedelta(days=i),
                value=1.0,
                estimated=False,
            )

            models.ConsumptionRecord.objects.create(
                metadata=gas,
                start=datetime(2011, 1, 1, tzinfo=pytz.UTC) + timedelta(days=i),
                value=1.0,
                estimated=False,
            )

        ## Attempt to run the meter
        cls.project.run_meter(start_date=make_aware(datetime(2011,1,1)), end_date=make_aware(datetime(2015,1,1)))
        cls.meter_runs = [models.MeterRun.objects.get(consumption_metadata=cm) for cm in cls.consumption_metadatas]
        assert len(cls.meter_runs) == 2

    def test_meter_run_read(self):
        """
        Tests reading meter run data.
        """
        for meter_run, consumption_metadata in zip(self.meter_runs,self.consumption_metadatas):

            response = self.get('/api/v1/meter_runs/{}/'.format(meter_run.id))
            assert response.status_code == 200

            fields = set([
                'id',
                'project',
                'consumption_metadata',
                'annual_savings',
                'gross_savings',
                'annual_usage_baseline',
                'annual_usage_reporting',
                'cvrmse_baseline',
                'cvrmse_reporting',
                'model_parameter_json_baseline',
                'model_parameter_json_reporting',
                'valid_meter_run',
                'meter_type',
                'fuel_type',
                'added',
                'updated',
            ])

            assert fields == set(response.data.keys())

    def test_meter_run_summary_read(self):
        """
        Tests reading meter run data.
        """
        for meter_run, consumption_metadata in zip(self.meter_runs,self.consumption_metadatas):

            response = self.get('/api/v1/meter_runs/{}/?summary=True'.format(meter_run.id))
            assert response.status_code == 200

            fields = set([
                'id',
                'project',
                'consumption_metadata',
                'meter_type',
                'annual_usage_baseline',
                'annual_usage_reporting',
                'annual_savings',
                'gross_savings',
                'cvrmse_baseline',
                'cvrmse_reporting',
                'valid_meter_run',
                'added',
                'updated',
            ])

            assert fields == set(response.data.keys())

    def test_meter_run_monthly_read(self):
        """
        Tests reading meter run data.
        """
        for meter_run, consumption_metadata in zip(self.meter_runs,self.consumption_metadatas):

            response = self.get('/api/v1/meter_runs/{}/?monthly=True'.format(meter_run.id))
            assert response.status_code == 200

            fields = set([
                'id',
                'project',
                'consumption_metadata',
                'annual_savings',
                'gross_savings',
                'annual_usage_baseline',
                'annual_usage_reporting',
                'cvrmse_baseline',
                'cvrmse_reporting',
                'model_parameter_json_baseline',
                'model_parameter_json_reporting',
                'valid_meter_run',
                'meter_type',
                'fuel_type',
                'added',
                'updated',
                'monthlyaverageusagebaseline_set',
                'monthlyaverageusagereporting_set',
            ])

            assert fields == set(response.data.keys())

    def test_meter_run_daily_read(self):
        """
        Tests reading meter run data.
        """
        for meter_run, consumption_metadata in zip(self.meter_runs,self.consumption_metadatas):

            response = self.get('/api/v1/meter_runs/{}/?daily=True'.format(meter_run.id))
            assert response.status_code == 200

            fields = set([
                'id',
                'project',
                'consumption_metadata',
                'annual_savings',
                'gross_savings',
                'annual_usage_baseline',
                'annual_usage_reporting',
                'cvrmse_baseline',
                'cvrmse_reporting',
                'model_parameter_json_baseline',
                'model_parameter_json_reporting',
                'valid_meter_run',
                'meter_type',
                'fuel_type',
                'added',
                'updated',
                'dailyusagebaseline_set',
                'dailyusagereporting_set',
            ])

            assert fields == set(response.data.keys())
