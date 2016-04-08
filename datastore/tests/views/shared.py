from django.utils.timezone import now, timedelta
from django.test import Client, TestCase
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken, get_application_model

import json
from datastore import models

ApplicationModel = get_application_model()

class OAuthTestCase(TestCase):

    def setUp(self):
        """
        Includes a client, a demo user/project_owner, an application model
        and an Oauth token.
        """
        self.client = Client()
        self.user = User.objects.create_user("username", "user@example.com", "123456")
        self.project_owner = self.user.projectowner

        self.project = models.Project.objects.create(
            project_owner=self.project_owner,
            project_id="ABC",
        )

        self.app = ApplicationModel.objects.create(
            name='app',
            client_type=ApplicationModel.CLIENT_CONFIDENTIAL,
            authorization_grant_type=ApplicationModel.GRANT_CLIENT_CREDENTIALS,
            user=self.user
        )

        self.token = AccessToken.objects.create(
            user=self.user,
            token='tokstr',
            application=self.app,
            expires=now() + timedelta(days=365),
            scope="read write"
        )


    def tearDown(self):
        """
        Removes persistent data from the datastore
        after running tests.
        """
        self.user.delete()
        self.project_owner.delete()
        self.project.delete()
        self.app.delete()
        self.token.delete()

    def post(self, url, data):
        return self.client.post(url, json.dumps(data),
                                content_type="application/json",
                                Authorization="Bearer " + "tokstr")

    def get(self, url):
        return self.client.get(url, Authorization="Bearer " + "tokstr")
