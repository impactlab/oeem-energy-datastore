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

class MeterRunAPITestCase(OAuthTestCase):

    def setUp(self):
        """
        Setup methods for a eemeter run storage
        engine.
        """
        super(MeterRunAPITestCase,self).setUp()

        zipcode = "91104"
        project = get_example_project(zipcode)

        self.project = models.Project(
            project_owner=self.project_owner,
            project_id="TEST_PROJECT",
            baseline_period_start=project.baseline_period.start,
            baseline_period_end=project.baseline_period.end,
            reporting_period_start=project.reporting_period.start,
            reporting_period_end=project.reporting_period.end,
            zipcode=None,
            weather_station=project.location.station,
            latitude=None,
            longitude=None,
        )
        self.project.save()

        fuel_types = {"electricity": "E", "natural_gas": "NG"}
        energy_units = {"kWh": "KWH", "therm": "THM"}

        self.consumption_metadatas = []
        for consumption_data in project.consumption:
            consumption_metadata = models.ConsumptionMetadata(
                    project=self.project,
                    fuel_type=fuel_types[consumption_data.fuel_type],
                    energy_unit=energy_units[consumption_data.unit_name])
            consumption_metadata.save()
            self.consumption_metadatas.append(consumption_metadata)

            for record in consumption_data.records(record_type="arbitrary_start"):
                record = models.ConsumptionRecord(metadata=consumption_metadata,
                    start=record["start"].isoformat(),
                    value=record["value"],
                    estimated=False)
                record.save()

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
