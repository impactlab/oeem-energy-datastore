from django.test import TestCase
from django.contrib.auth.models import User

import pytest

from datastore import models


class ProjectBlockTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            'john', 'lennon@thebeatles.com', 'johnpassword')

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
        with pytest.raises(AttributeError):
            self.project_block.run_meters()
