from django.test import TestCase
from django.contrib.auth.models import User

from datetime import datetime, timedelta
import tempfile

from eemeter.structures import (
    Project,
    ModelingPeriod,
    ZIPCodeSite,
)
from eemeter.testing.mocks import MockWeatherClient
from eemeter.weather import TMY3WeatherSource, ISDWeatherSource
import numpy as np
from numpy.testing import assert_allclose
import pytz

from datastore import models

class ProjectTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        cls.project = models.Project.objects.create(
            project_owner=cls.user.projectowner,
            project_id="PROJECTID_1",
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
            "weather_station",
            "latitude",
            "longitude",
            "added",
            "updated",
        ]
        for attribute in attributes:
            assert hasattr(self.project, attribute)

    def test_lat_lng(self):
        lat_lng = self.project.lat_lng
        assert len(lat_lng) == 2

    def test_eemeter_project(self):

        eemeter_project = self.project.eemeter_project()
        assert isinstance(eemeter_project, Project)

    def test_run_meter(self):

        project_result = self.project.run_meter(weather_source=self.weather_source,
                               weather_normal_source=self.weather_normal_source)

        assert project_result.eemeter_version == "0.3.20"
        assert project_result.meter_class == "EnergyEfficiencyMeter"
        assert isinstance(project_result.project_id, int)
        assert project_result.meter_settings is None

        assert len(project_result.derivative_aggregations.all()) == 3
        assert len(project_result.energy_trace_model_results.all()) == 4
        assert len(project_result.modeling_periods.all()) == 2
        assert len(project_result.modeling_period_groups.all()) == 1
