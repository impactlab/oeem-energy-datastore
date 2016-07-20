from django.utils.timezone import now, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken, get_application_model
from datetime import datetime
import pytz
from datastore.services import create_project

ApplicationModel = get_application_model()


class Command(BaseCommand):
    help = "Initialize the datastore for development"

    def handle(self, *args, **options):
        # create a superuser
        user = User.objects.create_superuser('demo', 'demo@example.com',
                                             'demo-password')
        user.save()

        app = ApplicationModel.objects.create(
            name='app',
            client_type=ApplicationModel.CLIENT_CONFIDENTIAL,
            authorization_grant_type=ApplicationModel.GRANT_CLIENT_CREDENTIALS,
            user=user
        )

        AccessToken.objects.create(
            user=user,
            token='tokstr',
            application=app,
            expires=now() + timedelta(days=365),
            scope="read write"
        )

        create_project(spec={
            "project_id": "ABC",
            "project_owner": user.projectowner,
            "baseline_period_end": datetime(2012, 1, 1, tzinfo=pytz.UTC),
            "reporting_period_start": datetime(2012, 2, 1, tzinfo=pytz.UTC),
            "zipcode": "91104",
            "traces": [
                {
                    "interpretation": "NG_C_S",
                    "unit": "THM",
                    "start": "2010-01-01",
                    "end": "2014-12-31",
                    "freq": "MS",
                    "value": 1,
                    "nans": set(range(0, 60, 20)),
                    "estimated": set(range(3, 60, 15)),
                },
                {
                    "interpretation": "NG_C_S",
                    "unit": "THM",
                    "start": "2011-09-01",
                    "end": "2014-12-31",
                    "freq": "D",
                    "value": 2,
                    "nans": set(range(0, 1000, 20)),
                    "estimated": set(range(3, 1000, 15)),
                },
                {
                    "interpretation": "E_C_S",
                    "unit": "KWH",
                    "start": "2011-01-01",
                    "end": "2014-12-31",
                    "freq": "15T",
                    "value": 0.04,
                    "nans": set(range(0, 96*365*4, 200)),
                    "estimated": set(range(3, 96*365*4, 150)),
                },
                {
                    "interpretation": "E_C_S",
                    "unit": "KWH",
                    "start": "2011-01-01",
                    "end": "2014-12-31",
                    "freq": "H",
                    "value": 0.4,
                    "nans": set(range(0, 96*365*4, 200)),
                    "estimated": set(range(3, 96*365*4, 150)),
                },
                {
                    "interpretation": "E_OSG_U",
                    "unit": "KWH",
                    "start": "2012-01-15",
                    "end": "2014-12-31",
                    "freq": "H",
                    "value": 0.3,
                    "nans": set(range(0, 96*365*4, 200)),
                    "estimated": set(range(3, 96*365*4, 150)),
                },
                {
                    "interpretation": "E_OSG_U",
                    "unit": "KWH",
                    "start": "2010-01-01",
                    "end": "2014-12-31",
                    "freq": "30T",
                    "value": 0.1,
                    "nans": set(range(0, 96*365*4, 200)),
                    "estimated": set(range(3, 96*365*4, 150)),
                },
            ],
        })
