from django.test import TestCase
from django.contrib.auth.models import User

from datastore import models

from datetime import datetime, date

class ProjectAttributesTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        project = models.Project.objects.create(
            project_owner=user.projectowner,
            project_id="PROJECTID_3",
        )

        boolean_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME1",
            display_name="DISPLAYNAME",
            data_type="BOOLEAN",
        )
        self.boolean_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=boolean_project_attribute_key,
            boolean_value=True,
        )

        char_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME2",
            display_name="DISPLAYNAME",
            data_type="CHAR",
        )
        self.char_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=char_project_attribute_key,
            char_value="Test",
        )

        date_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME3",
            display_name="DISPLAYNAME",
            data_type="DATE",
        )
        self.date_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=date_project_attribute_key,
            date_value=date(2011, 1, 1),
        )

        datetime_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME4",
            display_name="DISPLAYNAME",
            data_type="DATETIME",
        )
        self.datetime_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=datetime_project_attribute_key,
            datetime_value=datetime(2011, 1, 1),
        )

        float_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME5",
            display_name="DISPLAYNAME",
            data_type="FLOAT",
        )
        self.float_project_attribute = models.ProjectAttribute.objects.create(
            project=project,
            key=float_project_attribute_key,
            float_value=0.1,
        )

        integer_project_attribute_key = models.ProjectAttributeKey.objects.create(
            name="NAME6",
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

