from django.test import TestCase
from django.contrib.auth.models import User

from datastore import models

from eemeter.structures import EnergyTrace


class ConsumptionMetadataTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com',
                                        'johnpassword')
        project = models.Project.objects.create(
            project_owner=user.projectowner,
            project_id="PROJECTID_6",
        )
        self.consumptionmetadata = models.ConsumptionMetadata.objects.create(
            project=project,
            interpretation="E_C_S",
            unit="KWH",
        )

    def test_attributes(self):
        attributes = [
            "interpretation",
            "unit",
            "project",
            "added",
            "updated",
        ]
        for attribute in attributes:
            assert hasattr(self.consumptionmetadata, attribute)

    def test_eemeter_consumption_data(self):
        trace = self.consumptionmetadata.eemeter_consumption_data()
        assert isinstance(trace, EnergyTrace)
