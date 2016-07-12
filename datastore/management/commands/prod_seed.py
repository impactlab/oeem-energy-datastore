import string
import random
import logging
from django.utils.timezone import now, timedelta
from django.core.management.base import BaseCommand
from datastore.models import *
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken, get_application_model
from datetime import datetime

ApplicationModel = get_application_model()

class Command(BaseCommand):
    help = "Initialize the datastore on production"

    def handle(self, *args, **options):

        def random_string(N):
            return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

        password = random_string(12)
        token = random_string(12)

        # create a superuser
        user = User.objects.create_superuser('admin', 'admin@openee.io', password)
        user.save()

        app = ApplicationModel.objects.create(
            name='app',
            client_type=ApplicationModel.CLIENT_CONFIDENTIAL,
            authorization_grant_type=ApplicationModel.GRANT_CLIENT_CREDENTIALS,
            user=user
        )

        token = AccessToken.objects.create(
            user=user,
            token=token,
            application=app,
            expires=now() + timedelta(days=365),
            scope="read write"
        )

        print("Admin password: %s" % password)
        print("Admin token: %s" % token)