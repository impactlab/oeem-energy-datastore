from django.test import TestCase

from ..models import ConsumptionMetadata
from ..models import ConsumptionRecord
from ..models import ProjectOwner
from ..models import Project
from ..models import ProjectBlock
from ..models import FuelTypeSummary

from eemeter.consumption import ConsumptionData as EEMeterConsumptionData
from eemeter.project import Project as EEMeterProject
from eemeter.examples import get_example_project
from eemeter.evaluation import Period

from datetime import datetime
import pytz

import pytest

class ProjectBlockTestCase(TestCase):

    fixtures = ['testing.yaml']

    def setUp(self):
        self.project_block = ProjectBlock.objects.all()[0]

    def test_project_block_run_meters(self):
        for project in self.project_block.project.all():
            assert len(project.meterrun_set.all()) == 0
        self.project_block.run_meters()
        for project in self.project_block.project.all():
            assert len(project.meterrun_set.all()) == 2

    def test_project_block_compute_summary_timeseries(self):
        self.project_block.run_meters(end_date=datetime(2015,1,1,tzinfo=pytz.utc))
        assert len(self.project_block.fueltypesummary_set.all()) == 0
        self.project_block.compute_summary_timeseries()
        assert len(self.project_block.fueltypesummary_set.all()) == 2
        assert len(self.project_block.fueltypesummary_set.all()[0] \
                .dailyusagesummarybaseline_set.all()) == 1461
        assert len(self.project_block.fueltypesummary_set.all()[0] \
                .dailyusagesummaryactual_set.all()) == 1461
        assert len(self.project_block.fueltypesummary_set.all()[0] \
                .dailyusagesummaryreporting_set.all()) == 1461

        assert len(self.project_block.fueltypesummary_set.all()[0] \
                .monthlyusagesummarybaseline_set.all()) == 48
        assert len(self.project_block.fueltypesummary_set.all()[0] \
                .monthlyusagesummaryactual_set.all()) == 48
        assert len(self.project_block.fueltypesummary_set.all()[0] \
                .monthlyusagesummaryreporting_set.all()) == 48

    def test_project_block_recent_summaries(self):
        self.project_block.run_meters()
        self.project_block.compute_summary_timeseries()
        self.project_block.compute_summary_timeseries()
        recent_summaries = self.project_block.recent_summaries()
        assert len(recent_summaries) == 2
        for summary in recent_summaries:
            assert isinstance(summary, FuelTypeSummary)

class ConsumptionTestCase(TestCase):

    fixtures = ["testing.yaml"]

    def setUp(self):
        self.consumption_metadata = ConsumptionMetadata.objects.all()[0]
        self.record = ConsumptionRecord.objects.all()[0]

    def test_consumption_eemeter_consumption_data(self):
        consumption_data = self.consumption_metadata.eemeter_consumption_data()
        assert isinstance(consumption_data, EEMeterConsumptionData)

    def test_consumption_eemeter_record(self):
        record = self.record.eemeter_record()
        assert isinstance(record, dict)
        assert record["start"] == self.record.start
        assert record["value"] == self.record.value
        assert record["estimated"] == self.record.estimated
        assert len(record) == 3

class ProjectTestCase(TestCase):

    fixtures = ["testing.yaml"]

    def setUp(self):
        self.project = Project.objects.all()[0]

    def test_project_baseline_period(self):
        period = self.project.baseline_period
        assert isinstance(period, Period)
        assert isinstance(period.start, datetime)
        assert isinstance(period.end, datetime)

    def test_project_reporting_period(self):
        period = self.project.reporting_period
        assert isinstance(period, Period)
        assert isinstance(period.start, datetime)
        assert isinstance(period.end, datetime)

    def test_project_lat_lng(self):
        assert self.project.lat_lng is None
        self.project.latitude = 41.8
        self.project.longitude = -87.6
        assert self.project.lat_lng is not None

    def test_project_eemeter_project_with_zipcode(self):
        self.project.zipcode = "91104"
        project, cm_ids = self.project.eemeter_project()
        assert isinstance(project, EEMeterProject)
        assert len(cm_ids) == 2

    def test_project_eemeter_project_with_lat_lng(self):
        self.project.latitude = 34.16
        self.project.longitude = -118.12
        project, cm_ids = self.project.eemeter_project()
        assert isinstance(project, EEMeterProject)
        assert len(cm_ids) == 2

    def test_project_eemeter_project_with_station(self):
        self.project.weather_station = "722880"
        project, cm_ids = self.project.eemeter_project()
        assert isinstance(project, EEMeterProject)
        assert len(cm_ids) == 2

    def test_project_run_meter(self):
        assert len(self.project.meterrun_set.all()) == 0

        # set up project
        self.project.weather_station = "722880"

        # run meter
        self.project.run_meter()

        assert len(self.project.meterrun_set.all()) == 2

    def test_project_recent_meter_runs(self):

        # set up project
        self.project.weather_station = "722880"

        # run meter
        self.project.run_meter()
        assert len(self.project.meterrun_set.all()) == 2

        self.project.run_meter()
        assert len(self.project.meterrun_set.all()) == 4

        recent_meter_runs = self.project.recent_meter_runs()
        assert len(recent_meter_runs) == 2
