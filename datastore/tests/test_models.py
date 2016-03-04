from django.test import TestCase
from django.contrib.auth.models import User

from .. import models

import eemeter.consumption
import eemeter.project
import eemeter.evaluation

from datetime import datetime, date
import pytz

class ProjectOwnerTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

    def test_project_owner_auto_create(self):
        assert self.user.projectowner.user == self.user


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

class ProjectAttributesTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        project = models.Project.objects.create(
            project_owner=user.projectowner,
            project_id="PROJECTID_3",
        )

        boolean_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME",
            display_name="DISPLAYNAME",
            data_type="BOOLEAN",
        )
        self.boolean_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=boolean_project_attribute_key,
            boolean_value=True,
        )

        char_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME",
            display_name="DISPLAYNAME",
            data_type="CHAR",
        )
        self.char_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=char_project_attribute_key,
            char_value="Test",
        )

        date_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME",
            display_name="DISPLAYNAME",
            data_type="DATE",
        )
        self.date_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=date_project_attribute_key,
            date_value=date(2011, 1, 1),
        )

        datetime_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME",
            display_name="DISPLAYNAME",
            data_type="DATETIME",
        )
        self.datetime_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=datetime_project_attribute_key,
            datetime_value=datetime(2011, 1, 1),
        )

        float_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME",
            display_name="DISPLAYNAME",
            data_type="FLOAT",
        )
        self.float_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=float_project_attribute_key,
            float_value=0.1,
        )

        integer_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME",
            display_name="DISPLAYNAME",
            data_type="INTEGER",
        )
        self.integer_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=integer_project_attribute_key,
            integer_value=1,
        )

    def test_values(self):
        assert self.boolean_project_attribute.value() == True
        assert self.char_project_attribute.value() == "Test"
        assert self.date_project_attribute.value() == date(2011, 1, 1)
        assert self.datetime_project_attribute.value() == datetime(2011, 1, 1)
        assert self.float_project_attribute.value() == 0.1
        assert self.integer_project_attribute.value() == 1


class ProjectBlockTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        project1 = models.Project.objects.create(
            project_owner=user.projectowner,
            project_id="PROJECTID_4",
        )
        project2 = models.Project.objects.create(
            project_owner=user.projectowner,
            project_id="PROJECTID_5",
        )

        self.project_block = models.ProjectBlock.objects.create(
            name="NAME",
        )
        self.project_block.projects.add(project1)
        self.project_block.projects.add(project2)

    def test_attributes(self):
        attributes = [
            "name",
            "projects",
            "added",
            "updated",
        ]
        for attribute in attributes:
            assert hasattr(self.project_block, attribute)

    def test_run_meters(self):
        self.project_block.run_meters()

    def test_recent_summaries(self):
        recent_summaries = self.project_block.recent_summaries()

class ConsumptionMetadataTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        project = models.Project.objects.create(
            project_owner=user.projectowner,
            project_id="PROJECTID_6",
        )
        self.consumptionmetadata = models.ConsumptionMetadata.objects.create(
            project=project,
            fuel_type="E",
            energy_unit="KWH",
        )


    def test_attributes(self):
        attributes = [
            "fuel_type",
            "energy_unit",
            "project",
            "added",
            "updated",
        ]
        for attribute in attributes:
            assert hasattr(self.consumptionmetadata, attribute)

    def test_eemeter_consumption_data(self):
        consumption_data = self.consumptionmetadata.eemeter_consumption_data()
        assert isinstance(consumption_data, eemeter.consumption.ConsumptionData)


class ConsumptionRecordTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        project = models.Project.objects.create(
            project_owner=user.projectowner,
            project_id="PROJECTID_6",
        )
        consumptionmetadata = models.ConsumptionMetadata.objects.create(
            project=project,
            fuel_type="E",
            energy_unit="KWH",
        )
        self.consumptionrecord = models.ConsumptionRecord.objects.create(
            metadata=consumptionmetadata,
            start=datetime(2011, 1, 1),
            value=0.0,
            estimated=True,
        )

    def test_attributes(self):
        attributes = [
            "metadata",
            "start",
            "value",
            "estimated",
        ]
        for attribute in attributes:
            assert hasattr(self.consumptionrecord, attribute)

    def test_eemeter_record(self):
        record = self.consumptionrecord.eemeter_record()
        assert isinstance(record, dict)

class MeterRunTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        project = models.Project.objects.create(
            project_owner=user.projectowner,
            project_id="PROJECTID_6",
        )
        consumptionmetadata = models.ConsumptionMetadata.objects.create(
            project=project,
            fuel_type="E",
            energy_unit="KWH",
        )
        self.meterrun = models.MeterRun.objects.create(
            project=project,
            consumption_metadata=consumptionmetadata,
        )

    def test_attributes(self):
        attributes = [
            "project",
            "consumption_metadata",
            "serialization",
            "annual_usage_baseline",
            "annual_usage_reporting",
            "gross_savings",
            "annual_savings",
            "meter_type",
            "model_parameter_json_baseline",
            "model_parameter_json_reporting",
            "cvrmse_baseline",
            "cvrmse_reporting",
            "added",
            "updated",
        ]
        for attribute in attributes:
            assert hasattr(self.meterrun, attribute)

    def test_valid_meter_run(self):
        assert self.meterrun.valid_meter_run() == False
