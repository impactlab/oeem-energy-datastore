from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now

from ..models import ConsumptionMetadata
from ..models import ConsumptionRecord
from ..models import ProjectOwner
from ..models import Project

from eemeter.consumption import ConsumptionData as EEMeterConsumptionData
from eemeter.project import Project as EEMeterProject
from eemeter.examples import get_example_project
from eemeter.evaluation import Period

from datetime import datetime

class ConsumptionTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("user", "test@user.com", "123456")
        self.consumption_metadata = ConsumptionMetadata(fuel_type="E", energy_unit="KWH")
        self.consumption_metadata.save()
        self.record = ConsumptionRecord(
            metadata=self.consumption_metadata, start=now(), estimated=False)
        self.record.save()

    def tearDown(self):
        self.user.delete()

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

    def setUp(self):
        self.user = User.objects.create_user("user", "test@user.com", "123456")
        self.project_owner = ProjectOwner(user=self.user)
        self.project_owner.save()

        project = get_example_project("91104")

        self.project = Project(
                project_owner=self.project_owner,
                project_id="TEST_PROJECT",
                baseline_period_start=project.baseline_period.start,
                baseline_period_end=project.baseline_period.end,
                reporting_period_start=project.reporting_period.start,
                reporting_period_end=project.reporting_period.end,
                zipcode=None,
                weather_station=None,
                latitude=None,
                longitude=None,
                )
        self.project.save()

        fuel_types = {"electricity": "E", "natural_gas": "NG"}
        energy_units = {"kWh": "KWH", "therm": "THM"}

        self.consumption_metadatas = []
        for consumption_data in project.consumption:
            consumption_metadata = ConsumptionMetadata(
                    project=self.project,
                    fuel_type=fuel_types[consumption_data.fuel_type],
                    energy_unit=energy_units[consumption_data.unit_name])
            consumption_metadata.save()
            self.consumption_metadatas.append(consumption_metadata)

            for record in consumption_data.records(record_type="arbitrary_start"):
                record = ConsumptionRecord(metadata=consumption_metadata,
                    start=record["start"].isoformat(),
                    value=record["value"],
                    estimated=False)
                record.save()

    def tearDown(self):
        self.user.delete()
        self.project_owner.delete()
        self.project.delete()
        for c in self.consumption_metadatas:
            c.delete()

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
