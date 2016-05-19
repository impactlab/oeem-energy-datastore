from django.utils.timezone import now, timedelta
from django.test import Client, TestCase
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken, get_application_model

import json
from datastore import models

ApplicationModel = get_application_model()

class OAuthTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Includes a client, a demo user/project_owner, an application model
        and an Oauth token.
        """
        super(OAuthTestCase, cls).setUpTestData()

        cls.client = Client()
        cls.user = User.objects.create_user("username", "user@example.com", "123456")
        cls.project_owner = cls.user.projectowner

        cls.project = models.Project.objects.create(
            project_owner=cls.project_owner,
            project_id="ABC",
        )

        self.project2 = models.Project.objects.create(
            project_owner=self.project_owner,
            project_id="DEF",
        )

        self.app = ApplicationModel.objects.create(
            name='app',
            client_type=ApplicationModel.CLIENT_CONFIDENTIAL,
            authorization_grant_type=ApplicationModel.GRANT_CLIENT_CREDENTIALS,
            user=cls.user
        )

        cls.token = AccessToken.objects.create(
            user=cls.user,
            token='tokstr',
            application=cls.app,
            expires=now() + timedelta(days=365),
            scope="read write"
        )


    @classmethod
    def tearDownClass(cls):
        """
        Removes persistent data from the datastore
        after running tests.
        """

        cls.user.delete()
        cls.project_owner.delete()
        cls.project.delete()
        cls.app.delete()
        cls.token.delete()

        super(OAuthTestCase, cls).tearDownClass()

    def post(self, url, data):
        return self.client.post(url, json.dumps(data),
                                content_type="application/json",
                                Authorization="Bearer " + "tokstr")

    def get(self, url, data=None):
        return self.client.get(url, Authorization="Bearer " + "tokstr", data=data)
