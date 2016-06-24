from django.test import TestCase
from django.contrib.auth.models import User

from datastore import models, services

class ExportServiceTestCase(TestCase):

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

    def test_export(self):
        data = services.meterruns_export()
        assert 'headers' in data
        assert 'meter_runs' in data
        assert len(data['meter_runs']) == 1
