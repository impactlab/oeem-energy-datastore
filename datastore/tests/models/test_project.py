from django.test import TestCase
from django.contrib.auth.models import User

from datetime import datetime
import tempfile

from eemeter.structures import (
    Project,
)
from eemeter.testing.mocks import MockWeatherClient
from eemeter.weather import TMY3WeatherSource, ISDWeatherSource
import pytz

from datastore.services import create_project


class ProjectTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user('john', 'lennon@thebeatles.com',
                                            'johnpassword')

        cls.project = create_project(spec={
            "project_id": "ABCD",
            "project_owner": cls.user.projectowner,
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

        tmp_dir = tempfile.mkdtemp()
        wns = TMY3WeatherSource("724838", tmp_dir, preload=False)
        wns.client = MockWeatherClient()
        wns._load_data()
        cls.weather_normal_source = wns

        tmp_dir = tempfile.mkdtemp()
        ws = ISDWeatherSource("722880", tmp_dir)
        ws.client = MockWeatherClient()
        cls.weather_source = ws

    def test_attributes(self):
        attributes = [
            "project_owner",
            "project_id",
            "baseline_period_start",
            "baseline_period_end",
            "reporting_period_start",
            "reporting_period_end",
            "zipcode",
            "added",
            "updated",
        ]
        for attribute in attributes:
            assert hasattr(self.project, attribute)

    def test_eemeter_project(self):

        eemeter_project = self.project.eemeter_project()
        assert isinstance(eemeter_project, Project)

    def test_run_meter(self):

        project_result = self.project.run_meter(
            weather_source=self.weather_source,
            weather_normal_source=self.weather_normal_source)

        assert project_result.eemeter_version == "0.4.1"
        assert project_result.meter_class == "EnergyEfficiencyMeter"
        assert isinstance(project_result.project_id, int)
        assert project_result.meter_settings is None

        assert len(project_result.derivative_aggregations.all()) == 8
        assert len(project_result.energy_trace_model_results.all()) == 12
        assert len(project_result.modeling_periods.all()) == 2
        assert len(project_result.modeling_period_groups.all()) == 1
