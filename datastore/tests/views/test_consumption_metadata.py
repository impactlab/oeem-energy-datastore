from .shared import OAuthTestCase
from datastore import models

class ConsumptionMetadataAPITestCase(OAuthTestCase):

    def test_consumption_metadata_create_read(self):
        consumption_data = {
            "interpretation": "E_C_S",
            "unit": "KWH",
        }

        response = self.post(
            '/api/v1/consumption_metadatas/?summary=True', consumption_data)

        assert response.status_code == 201

        assert isinstance(response.data['id'], int)
        assert response.data['unit'] == 'KWH'
        assert response.data['interpretation'] == 'E_C_S'
        assert response.data['project'] is None
        assert 'records' not in response.data

        consumption_metadata_id = response.data['id']
        response = self.get(
            '/api/v1/consumption_metadatas/{}/'
            .format(consumption_metadata_id)
        )

        assert response.status_code == 200

        assert response.data['id'] == consumption_metadata_id
        assert response.data['unit'] == 'KWH'
        assert response.data['interpretation'] == 'E_C_S'
        assert response.data['project'] is None


    def test_consumption_metadata_create_read_many(self):

        # Test that two objects are created
        post_body = [{
            "interpretation": "E_C_S",
            "unit": "KWH",
            "label": "0",
            "project_project_id": "ABC",
        }, {
            "interpretation": "E_C_S",
            "unit": "KWH",
            "label": "1",
            "project_project_id": "ABC",
        }]

        project_id = models.Project.objects.get(project_id="ABC").pk

        response = self.post(
            '/api/v1/consumption_metadatas/many/', post_body)

        assert response.status_code == 201

        assert len(response.data) == 2

        for record in response.data:
            assert isinstance(record['id'], int)
            assert record['unit'] == 'KWH'
            assert record['interpretation'] == 'E_C_S'
            assert record['project'] == project_id

        # Test updating using `label` to identify the record
        id = response.data[0]['id']
        label = response.data[0]['label']

        post_body = [{
            "unit": "THM",
            "interpretation": "E_C_S",
            "label": label,
        }]

        response = self.post(
            '/api/v1/consumption_metadatas/many/', post_body)

        response = self.get(
            '/api/v1/consumption_metadatas/{}/'
            .format(id)
        )

        assert response.status_code == 200

        assert response.data['id'] == id
        assert response.data['label'] == label
        assert response.data['unit'] == 'THM'






