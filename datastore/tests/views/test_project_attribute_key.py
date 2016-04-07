from .shared import OAuthTestCase

from datastore import models

class ProjectAttributeKeyAPITestCase(OAuthTestCase):

    def test_project_attribute_key_create_read(self):
        data = {
            'name': 'project_cost',
            'display_name': 'Project Cost',
            'data_type': 'FLOAT',
        }

        response = self.post('/api/v1/project_attribute_keys/', data)
        assert response.status_code == 201

        assert isinstance(response.data['id'], int)
        assert response.data['name'] == 'project_cost'
        assert response.data['display_name'] == 'Project Cost'
        assert response.data['data_type'] == 'FLOAT'

        project_attribute_key_id = response.data['id']
        response = self.get('/api/v1/project_attribute_keys/{}/'.format(project_attribute_key_id))
        assert response.status_code == 200

        assert isinstance(response.data['id'], int)
        assert response.data['name'] == 'project_cost'
        assert response.data['display_name'] == 'Project Cost'
        assert response.data['data_type'] == 'FLOAT'

