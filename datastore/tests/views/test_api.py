from .shared import OAuthTestCase
from django.utils.timezone import now, timedelta
from oauth2_provider.models import AccessToken


class ProjectAPITestCase(OAuthTestCase):

    def test_consumption_metatdata_bad_token(self):
        """
        Tests the oauth token againist the consumption
        API. Makes sure that that section of the
        API requires auth.
        """
        auth_headers = {"Authorization": "Bearer " + "badtoken"}
        response = self.client.get('/api/v1/', **auth_headers)
        assert response.status_code == 401
        assert response.data["detail"] == \
            "Authentication credentials were not provided."

    def test_consumption_metadata_bad_scope(self):
        """
        Tests for valid token being posted to /datastore/consumption
        endpoint. Basically a permissions test.
        """
        year_from_now = now() + timedelta(days=365)
        self.token = AccessToken.objects.create(user=self.user,
                                                token='tokstr_no_scope',
                                                application=self.app,
                                                expires=year_from_now)
        auth_headers = {"Authorization": "Bearer " + "tokstr_no_scope"}
        response = self.client.get('/api/v1/project_owners/', **auth_headers)
        assert response.status_code == 403
        assert response.data["detail"] == \
            "You do not have permission to perform this action."
