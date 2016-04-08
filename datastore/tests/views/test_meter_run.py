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

class MeterRunAPITestCase(OAuthTestCase):

    def setUp(self):
        """
        Setup methods for a eemeter run storage
        engine.
        """
        super(MeterRunAPITestCase,self).setUp()

        self.project = models.Project.objects.create(
            project_owner=self.user.projectowner,
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
            project=self.project,
            fuel_type="E",
            energy_unit="KWH",
        )

        gas = models.ConsumptionMetadata.objects.create(
            project=self.project,
            fuel_type="NG",
            energy_unit="THM",
        )

        self.consumption_metadatas = [elec, gas]

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
        self.project.run_meter(start_date=make_aware(datetime(2011,1,1)), end_date=make_aware(datetime(2015,1,1)))
        self.meter_runs = [models.MeterRun.objects.get(consumption_metadata=cm) for cm in self.consumption_metadatas]
        assert len(self.meter_runs) == 2

    def test_meter_run_read(self):
        """
        Tests reading meter run data.
        """
        for meter_run, consumption_metadata in zip(self.meter_runs,self.consumption_metadatas):

            response = self.get('/api/v1/meter_runs/{}/'.format(meter_run.id))
            assert response.status_code == 200
            assert response.data["project"] == self.project.id
            assert response.data["consumption_metadata"] == consumption_metadata.id

            model_parameters_baseline = json.loads(response.data["model_parameter_json_baseline"])
            model_parameters_reporting = json.loads(response.data["model_parameter_json_reporting"])

            assert type(model_parameters_baseline) == dict
            assert type(model_parameters_reporting) == dict

            assert len(response.data["serialization"]) > 7000

            assert len(response.data["dailyusagebaseline_set"]) == 1461
            assert len(response.data["dailyusagereporting_set"]) == 1461

            assert response.data["meter_type"] == "DFLT_RES_E" or \
                    response.data["meter_type"] == "DFLT_RES_NG"

            assert type(response.data["annual_usage_baseline"]) == float
            assert type(response.data["annual_usage_reporting"]) == float
            assert type(response.data["gross_savings"]) == float
            assert type(response.data["annual_savings"]) == float
            assert type(response.data["cvrmse_baseline"]) == float
            assert type(response.data["cvrmse_reporting"]) == float
