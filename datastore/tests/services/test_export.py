from django.test import TestCase
from django.contrib.auth.models import User

from datastore import models


class ExportServiceTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            'john', 'lennon@thebeatles.com', 'johnpassword')
        project = models.Project.objects.create(
            project_owner=user.projectowner,
            project_id="PROJECTID_6",
        )
        models.ConsumptionMetadata.objects.create(
            project=project,
            interpretation="E_C_S",
            unit="KWH",
        )

    def test_export(self):
        assert False
