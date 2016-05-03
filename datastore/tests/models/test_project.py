from django.test import TestCase
from django.contrib.auth.models import User

from datastore import models

from datetime import datetime, timedelta

import eemeter.project
import eemeter.evaluation

import pytz

class ProjectTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        self.empty_project = models.Project.objects.create(
            project_owner=self.user.projectowner,
            project_id="PROJECTID_1",
        )

        self.complete_project = models.Project.objects.create(
            project_owner=self.user.projectowner,
            project_id="PROJECTID_2",
            baseline_period_start=None,
            baseline_period_end=datetime(2012, 1, 1, tzinfo=pytz.UTC),
            reporting_period_start=datetime(2012, 2, 1, tzinfo=pytz.UTC),
            reporting_period_end=None,
            zipcode="91104",
            weather_station="722880",
            latitude=0,
            longitude=0,
        )

        consumptionmetadata = models.ConsumptionMetadata.objects.create(
            project=self.complete_project,
            fuel_type="E",
            energy_unit="KWH",
        )

        for i in range(0, 700, 30):
            models.ConsumptionRecord.objects.create(
                metadata=consumptionmetadata,
                start=datetime(2011, 1, 1, tzinfo=pytz.UTC) + timedelta(days=i),
                value=1.0,
                estimated=False,
            )


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
            assert hasattr(self.empty_project, attribute)

    def test_eemeter_baseline_period(self):
        empty_period = self.empty_project.eemeter_baseline_period()
        assert isinstance(empty_period, eemeter.evaluation.Period)

        complete_period = self.complete_project.eemeter_baseline_period()
        assert isinstance(complete_period, eemeter.evaluation.Period)

    def test_eemeter_reporting_period(self):
        empty_period = self.empty_project.eemeter_reporting_period()
        assert isinstance(empty_period, eemeter.evaluation.Period)

        complete_period = self.complete_project.eemeter_reporting_period()
        assert isinstance(complete_period, eemeter.evaluation.Period)

    def test_lat_lng(self):
        assert self.empty_project.lat_lng is None

        lat_lng = self.complete_project.lat_lng
        assert len(lat_lng) == 2

    def test_eemeter_location(self):
        with self.assertRaises(ValueError):
            self.empty_project.eemeter_location()

        location = self.complete_project.eemeter_location()
        assert isinstance(location, eemeter.location.Location)

    def test_eemeter_project(self):
        with self.assertRaises(ValueError):
            self.empty_project.eemeter_project()

        complete_eemeter_project, cm_ids = self.complete_project.eemeter_project()
        assert isinstance(complete_eemeter_project, eemeter.project.Project)
        assert len(cm_ids) == 1

    def test_run_meter_recent_meter_runs(self):

        meter_runs = models.Project.recent_meter_runs()
        assert meter_runs == {}

        self.empty_project.run_meter()
        self.complete_project.run_meter()

        meter_runs = list(models.Project.recent_meter_runs().items())
        assert len(meter_runs) == 1

        meter_run = meter_runs[0]
        assert isinstance(meter_run[0], int)
        assert meter_run[1][0]["fuel_type"] == "E"
        assert meter_run[1][0]["meterrun"] is not None

        self.complete_project.run_meter()

        meter_runs = list(models.Project.recent_meter_runs().items())
        assert len(meter_runs) == 1

        self.complete_project.meterrun_set.all().delete()
