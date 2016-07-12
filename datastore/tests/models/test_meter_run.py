from django.test import TestCase
from django.contrib.auth.models import User

from datastore import models

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
            unit="KWH",
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
            "meter_class",
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
