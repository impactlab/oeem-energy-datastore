from .shared import OAuthTestCase

from datastore import models

class ProjectAttributeAPITestCase(OAuthTestCase):

    def setUp(self):
        """
        Setup methods for a eemeter run storage
        engine.
        """
        super(ProjectAttributeAPITestCase,self).setUp()

        self.project_attribute_key = models.ProjectAttributeKey(
            name="project_cost",
            display_name="Project Cost",
            data_type="FLOAT",
        )
        self.project_attribute_key.save()

    def test_project_attribute_create_read(self):
        data = {
            'project': self.project.pk,
            'key': self.project_attribute_key.pk,
            'float_value': 0.0,
        }

        response = self.post('/api/v1/project_attributes/', data)
        assert response.status_code == 201

        assert isinstance(response.data['id'], int)
        assert response.data['key'] == self.project_attribute_key.pk
        assert response.data['project'] == self.project.pk
        assert response.data['date_value'] == None
        assert response.data['datetime_value'] == None
        assert response.data['boolean_value'] == None
        assert response.data['char_value'] == None
        assert response.data['value'] == 0.0
        assert response.data['float_value'] == 0.0
        assert response.data['integer_value'] == None

        project_attribute_id = response.data['id']
        response = self.get('/api/v1/project_attributes/{}/'.format(project_attribute_id))
        assert response.status_code == 200

        assert isinstance(response.data['id'], int)
        assert response.data['key'] == self.project_attribute_key.pk
        assert response.data['project'] == self.project.pk
        assert response.data['value'] == 0.0
