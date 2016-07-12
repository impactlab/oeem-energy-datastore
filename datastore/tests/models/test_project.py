from django.test import TestCase
from django.contrib.auth.models import User

from datetime import datetime, timedelta

from eemeter.structures import (
    Project,
    ModelingPeriod,
    ZIPCodeSite,
)
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

    def test_recent_meter_runs_emtpy(self):

        # empty because no meter runs yet.
        meter_runs = models.Project.recent_meter_runs()
        assert meter_runs == {}

    def test_recent_meter_runs_run_once(self):

        self.project.run_meter()

        meter_runs = models.Project.recent_meter_runs()
        assert len(meter_runs) == 1

        # get the one for the complete project
        project_meter_runs = meter_runs[self.project.pk]
        assert len(project_meter_runs) == 2

        gas_meter_run = project_meter_runs[self.cm_ng.pk]
        elec_meter_run = project_meter_runs[self.cm_e.pk]

        assert gas_meter_run["interpretation"] == "NG_C_S"
        assert elec_meter_run["interpretation"] == "E_C_S"

        assert isinstance(gas_meter_run["meter_run"], models.MeterRun)
        assert isinstance(elec_meter_run["meter_run"], models.MeterRun)

    def test_recent_meter_runs_run_twice(self):

        # run twice
        self.project.run_meter()
        self.project.run_meter()

        meter_runs = models.Project.recent_meter_runs()
        assert len(meter_runs) == 1

        # get the one for the complete project
        project_meter_runs = meter_runs[self.project.pk]
        assert len(project_meter_runs) == 2

        gas_meter_run = project_meter_runs[self.cm_ng.pk]
        elec_meter_run = project_meter_runs[self.cm_e.pk]

        assert gas_meter_run["interpretation"] == "NG_C_S"
        assert elec_meter_run["interpretation"] == "E_C_S"

        assert isinstance(gas_meter_run["meter_run"], models.MeterRun)
        assert isinstance(elec_meter_run["meter_run"], models.MeterRun)

    def test_recent_meter_runs_with_parameters(self):
        self.project.run_meter()

        meter_runs = models.Project.recent_meter_runs()
        assert len(meter_runs) == 1

        # gets all
        meter_runs = models.Project.recent_meter_runs(project_pks=[])
        assert len(meter_runs) == 1

        # one for complete_project
        meter_runs = models.Project.recent_meter_runs(project_pks=[self.project.pk])
        assert self.project.pk in meter_runs

    def test_run_meter(self):
        meter_runs = models.Project.recent_meter_runs()
        assert meter_runs == {}

        self.project.run_meter()

        recent_meter_runs = models.Project.recent_meter_runs()
        assert len(recent_meter_runs) == 1

        project_meter_runs = recent_meter_runs[self.project.pk]
        assert len(project_meter_runs) == 2

        gas_meter_run = project_meter_runs[self.cm_ng.pk]["meter_run"]
        # assert_allclose(gas_meter_run.annual_savings, 0, rtol=1e-3, atol=1e-3)
        # assert_allclose(gas_meter_run.gross_savings, 0, rtol=1e-3, atol=1e-3)
        assert_allclose(gas_meter_run.cvrmse_baseline, 0.50748, rtol=1e-3, atol=1e-3)
        assert_allclose(gas_meter_run.cvrmse_reporting, 0.47151, rtol=1e-3, atol=1e-3)

        elec_meter_run = project_meter_runs[self.cm_e.pk]["meter_run"]
        # assert_allclose(elec_meter_run.annual_savings, 0, rtol=1e-3, atol=1e-3)
        # assert_allclose(elec_meter_run.gross_savings, 0, rtol=1e-3, atol=1e-3)
        assert_allclose(elec_meter_run.cvrmse_baseline, 0.24035, rtol=1e-3, atol=1e-3)
        assert_allclose(elec_meter_run.cvrmse_reporting, 0.33901, rtol=1e-3, atol=1e-3)
