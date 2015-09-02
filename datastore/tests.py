from django.test import Client, TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from oauth2_provider.models import AccessToken
from oauth2_provider.models import get_application_model
import json

ApplicationModel = get_application_model()

class OAuthTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user("user", "test@user.com", "123456")
        self.app = ApplicationModel.objects.create(
                    name='app',
                    client_type=ApplicationModel.CLIENT_CONFIDENTIAL,
                    authorization_grant_type=ApplicationModel.GRANT_CLIENT_CREDENTIALS,
                    user=self.user
                )
        self.token = AccessToken.objects.create(user=self.user,
                                                token='tokstr',
                                                application=self.app,
                                                expires=now() + timedelta(days=365),
                                                scope="read write")

    def tearDown(self):
            self.user.delete()
            self.app.delete()
            self.token.delete()

class ConsumptionMetadataAPITestCase(OAuthTestCase):

    def test_consumption_metatdata_bad_token(self):
        auth_headers = {"Authorization": "Bearer " + "badtoken" }
        response = self.client.get('/datastore/consumption/', **auth_headers)
        assert response.status_code == 401
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_consumption_metatdata_bad_scope(self):
        self.token = AccessToken.objects.create(user=self.user,
                                                token='tokstr_no_scope',
                                                application=self.app,
                                                expires=now() + timedelta(days=365))
        auth_headers = {"Authorization": "Bearer " + "tokstr_no_scope" }
        response = self.client.get('/datastore/consumption/', **auth_headers)
        assert response.status_code == 403
        assert response.data["detail"] == "You do not have permission to perform this action."

    def test_consumption_metatdata_create_read(self):
        auth_headers = { "Authorization": "Bearer " + "tokstr" }

        consumption_data = {
                "fuel_type": "E",
                "energy_unit": "KWH",
                "records": [{
                    "start": "2014-01-01T00:00:00+00:00",
                    "value": 0,
                    "estimated": False,
                }],
                }

        data = json.dumps(consumption_data)
        response = self.client.post('/datastore/consumption/', data, content_type="application/json", **auth_headers)

        assert response.status_code == 201
        assert response.data['energy_unit'] == 'KWH'
        assert response.data['fuel_type'] == 'E'
        assert isinstance(response.data['id'], int)
        assert len(response.data['records']) == 1

        consumption_metadata_id = response.data['id']
        response = self.client.get('/datastore/consumption/{}/'.format(consumption_metadata_id), **auth_headers)
        assert response.status_code == 200
        assert response.data['energy_unit'] == 'KWH'
        assert response.data['fuel_type'] == 'E'
        assert response.data['id'] == consumption_metadata_id
        assert len(response.data['records']) == 1
        assert response.data['records'][0]['start'] == "2014-01-01T00:00:00Z"
        assert response.data['records'][0]['value'] == 0
        assert response.data['records'][0]['estimated'] == False


    def test_project_create_read(self):
        pass
