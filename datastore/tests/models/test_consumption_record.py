from django.test import TestCase
from django.contrib.auth.models import User

from datastore import models

from datetime import datetime

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
            unit="KWH",
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
