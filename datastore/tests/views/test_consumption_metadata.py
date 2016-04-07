from django.utils.timezone import now, timedelta
from oauth2_provider.models import AccessToken
from .shared import OAuthTestCase
import json

class ConsumptionMetadataAPITestCase(OAuthTestCase):

    def test_consumption_metatdata_bad_token(self):
        """
        Tests the oauth token againist the consumption
        API. Makes sure that that section of the
        API requires auth.
        """
        auth_headers = {"Authorization": "Bearer " + "badtoken" }
        response = self.client.get('/api/v1/consumption_metadatas/', **auth_headers)
        assert response.status_code == 401
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_consumption_metadata_bad_scope(self):
        """
        Tests for valid token being posted to /datastore/consumption
        endpoint. Basically a permissions test.
        """
        self.token = AccessToken.objects.create(user=self.user,
                                                token='tokstr_no_scope',
                                                application=self.app,
                                                expires=now() + timedelta(days=365))
        auth_headers = {"Authorization": "Bearer " + "tokstr_no_scope" }
        response = self.client.get('/api/v1/consumption_metadatas/', **auth_headers)
        assert response.status_code == 403
        assert response.data["detail"] == "You do not have permission to perform this action."

    def test_consumption_metadata_create_read(self):
        """
        Tests if a user, with proper permissions, can
        create consumption data using the api at
        /datastore/consmption
        """
        auth_headers = { "Authorization": "Bearer " + "tokstr" }

        consumption_data = {
            "fuel_type": "E",
            "energy_unit": "KWH",
        }

        data = json.dumps(consumption_data)
        response = self.client.post('/api/v1/consumption_metadatas/?summary=True', data, content_type="application/json", **auth_headers)

        assert response.status_code == 201

        assert isinstance(response.data['id'], int)
        assert response.data['energy_unit'] == 'KWH'
        assert response.data['fuel_type'] == 'E'
        assert response.data['project'] == None

        consumption_metadata_id = response.data['id']
        response = self.client.get('/api/v1/consumption_metadatas/{}/'.format(consumption_metadata_id), **auth_headers)

        assert response.status_code == 200

        assert response.data['id'] == consumption_metadata_id
        assert response.data['energy_unit'] == 'KWH'
        assert response.data['fuel_type'] == 'E'
        assert response.data['project'] == None
        assert response.data['records'] == []

