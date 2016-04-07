from django.utils.timezone import now, timedelta
from django.test import Client, TestCase, RequestFactory
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken, get_application_model

ApplicationModel = get_application_model()

class OAuthTestCase(TestCase):

    def setUp(self):
        """
        Sets up the test cases. Includes a client,
        factory, a demo user, project owners, an application model
        and finally, a Oauth token.
        """
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user("username", "user@example.com", "123456")
        self.project_owner = self.user.projectowner
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
        """
        Removes persistent data from the datastore
        after running tests.
        """
        self.user.delete()
        self.project_owner.delete()
        self.app.delete()
        self.token.delete()

