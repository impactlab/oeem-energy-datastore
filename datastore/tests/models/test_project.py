from django.test import TestCase
from django.contrib.auth.models import User

from datastore import models

from datetime import datetime

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
            baseline_period_start=datetime(2000, 1, 1, tzinfo=pytz.UTC),
            baseline_period_end=datetime(2001, 1, 1, tzinfo=pytz.UTC),
            reporting_period_start=datetime(2002, 1, 1, tzinfo=pytz.UTC),
            reporting_period_end=datetime(2003, 1, 1, tzinfo=pytz.UTC),
            zipcode="ZIPCODE",
            weather_station="WEATHERSTA",
            latitude=0,
            longitude=0,
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

    def test_baseline_period(self):
        empty_period = self.empty_project.baseline_period
        assert isinstance(empty_period, eemeter.evaluation.Period)

        complete_period = self.complete_project.baseline_period
        assert isinstance(complete_period, eemeter.evaluation.Period)

    def test_reporting_period(self):
        empty_period = self.empty_project.reporting_period
        assert isinstance(empty_period, eemeter.evaluation.Period)

        complete_period = self.complete_project.reporting_period
        assert isinstance(complete_period, eemeter.evaluation.Period)

    def test_lat_lng(self):
        assert self.empty_project.lat_lng is None

        lat_lng = self.complete_project.lat_lng
        assert len(lat_lng) == 2

    def test_eemeter_project(self):
        with self.assertRaises(ValueError):
            self.empty_project.eemeter_project()

        complete_eemeter_project, cm_ids = self.complete_project.eemeter_project()
        assert isinstance(complete_eemeter_project, eemeter.project.Project)
        assert cm_ids == []

    def test_run_meter(self):

        self.empty_project.run_meter()
        self.complete_project.run_meter()

    def test_recent_meter_runs(self):
        meter_runs = self.empty_project.recent_meter_runs()
        assert meter_runs == []

        meter_runs = self.complete_project.recent_meter_runs()
        assert meter_runs == []
