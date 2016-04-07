from .shared import OAuthTestCase

class ConsumptionMetadataAPITestCase(OAuthTestCase):

    def test_consumption_metadata_create_read(self):
        consumption_data = {
            "fuel_type": "E",
            "energy_unit": "KWH",
        }

        response = self.post('/api/v1/consumption_metadatas/?summary=True', consumption_data)

        assert response.status_code == 201

        assert isinstance(response.data['id'], int)
        assert response.data['energy_unit'] == 'KWH'
        assert response.data['fuel_type'] == 'E'
        assert response.data['project'] == None

        consumption_metadata_id = response.data['id']
        response = self.get('/api/v1/consumption_metadatas/{}/'.format(consumption_metadata_id))

        assert response.status_code == 200

        assert response.data['id'] == consumption_metadata_id
        assert response.data['energy_unit'] == 'KWH'
        assert response.data['fuel_type'] == 'E'
        assert response.data['project'] == None
        assert response.data['records'] == []
