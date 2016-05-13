from django.test import TestCase
from django.contrib.auth.models import User

from datastore import models

from datetime import datetime, timedelta

import eemeter.project
import eemeter.evaluation

import numpy as np
from numpy.testing import assert_allclose

import pytz

class ProjectTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        cls.empty_project = models.Project.objects.create(
            project_owner=cls.user.projectowner,
            project_id="PROJECTID_1",
        )

        cls.complete_project = models.Project.objects.create(
            project_owner=cls.user.projectowner,
            project_id="PROJECTID_2",
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
            project=cls.complete_project,
            fuel_type="NG",
            energy_unit="THM",
        )

        cls.cm_e = models.ConsumptionMetadata.objects.create(
            project=cls.complete_project,
            fuel_type="E",
            energy_unit="KWH",
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
        assert len(cm_ids) == 2

    def test_recent_meter_runs_emtpy(self):

        # empty because no meter runs yet.
        meter_runs = models.Project.recent_meter_runs()
        assert meter_runs == {}

    def test_recent_meter_runs_run_once(self):

        self.empty_project.run_meter()
        self.complete_project.run_meter()

        meter_runs = models.Project.recent_meter_runs()
        assert len(meter_runs) == 1

        # get the one for the complete project
        project_meter_runs = meter_runs[self.complete_project.pk]
        assert len(project_meter_runs) == 2

        gas_meter_run = project_meter_runs[self.cm_ng.pk]
        elec_meter_run = project_meter_runs[self.cm_e.pk]

        assert gas_meter_run["fuel_type"] == "NG"
        assert elec_meter_run["fuel_type"] == "E"

        assert isinstance(gas_meter_run["meter_run"], models.MeterRun)
        assert isinstance(elec_meter_run["meter_run"], models.MeterRun)

    def test_recent_meter_runs_run_twice(self):

        # run twice
        self.complete_project.run_meter()
        self.complete_project.run_meter()

        meter_runs = models.Project.recent_meter_runs()
        assert len(meter_runs) == 1

        # get the one for the complete project
        project_meter_runs = meter_runs[self.complete_project.pk]
        assert len(project_meter_runs) == 2

        gas_meter_run = project_meter_runs[self.cm_ng.pk]
        elec_meter_run = project_meter_runs[self.cm_e.pk]

        assert gas_meter_run["fuel_type"] == "NG"
        assert elec_meter_run["fuel_type"] == "E"

        assert isinstance(gas_meter_run["meter_run"], models.MeterRun)
        assert isinstance(elec_meter_run["meter_run"], models.MeterRun)

    def test_recent_meter_runs_with_parameters(self):
        self.complete_project.run_meter()

        meter_runs = models.Project.recent_meter_runs()
        assert len(meter_runs) == 1

        # gets all
        meter_runs = models.Project.recent_meter_runs(project_pks=[])
        assert len(meter_runs) == 1

        # none for empty_project
        meter_runs = models.Project.recent_meter_runs(project_pks=[self.empty_project.pk])
        assert len(meter_runs) == 0

        # one for complete_project
        meter_runs = models.Project.recent_meter_runs(project_pks=[self.complete_project.pk])
        assert self.complete_project.pk in meter_runs

        # call from instances, same result
        meter_runs = self.empty_project.recent_meter_runs(project_pks=[self.complete_project.pk])
        assert self.complete_project.pk in meter_runs
        meter_runs = self.complete_project.recent_meter_runs(project_pks=[self.complete_project.pk])
        assert self.complete_project.pk in meter_runs

    def test_run_meter(self):
        meter_runs = models.Project.recent_meter_runs()
        assert meter_runs == {}

        self.complete_project.run_meter()

        recent_meter_runs = models.Project.recent_meter_runs()
        assert len(recent_meter_runs) == 1

        project_meter_runs = recent_meter_runs[self.complete_project.pk]
        assert len(project_meter_runs) == 2

        gas_meter_run = project_meter_runs[self.cm_ng.pk]["meter_run"]
        assert_allclose(gas_meter_run.annual_savings, 0, rtol=1e-3, atol=1e-3)
        assert_allclose(gas_meter_run.gross_savings, 0, rtol=1e-3, atol=1e-3)
        assert_allclose(gas_meter_run.cvrmse_baseline, 0, rtol=1e-3, atol=1e-3)
        assert_allclose(gas_meter_run.cvrmse_reporting, 0, rtol=1e-3, atol=1e-3)

        elec_meter_run = project_meter_runs[self.cm_e.pk]["meter_run"]
        assert_allclose(elec_meter_run.annual_savings, 0, rtol=1e-3, atol=1e-3)
        assert_allclose(elec_meter_run.gross_savings, 0, rtol=1e-3, atol=1e-3)
        assert_allclose(elec_meter_run.cvrmse_baseline, 0, rtol=1e-3, atol=1e-3)
        assert_allclose(elec_meter_run.cvrmse_reporting, 0, rtol=1e-3, atol=1e-3)
