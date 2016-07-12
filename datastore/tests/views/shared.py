from django.utils.timezone import now, timedelta
from django.test import Client, TestCase
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken, get_application_model

import json
from datetime import datetime, timedelta
import numpy as np
import pytz

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
            baseline_period_start=None,
            baseline_period_end=datetime(2012, 1, 1, tzinfo=pytz.UTC),
            reporting_period_start=datetime(2012, 1, 2, tzinfo=pytz.UTC),
            reporting_period_end=None,
            zipcode="91104",
            weather_station="722880",
            latitude=0,
            longitude=0,
        )

        cls.cm_ng = models.ConsumptionMetadata.objects.create(
            project=cls.project,
            interpretation="NG_C_S",
            unit="THM",
        )

        cls.cm_e = models.ConsumptionMetadata.objects.create(
            project=cls.project,
            interpretation="E_C_S",
            unit="KWH",
        )

        records = []

        for i in range(0, 700, 30):
            if i % 120 == 0:
                value = np.nan
            else:
                value = 1.0
            records.append(models.ConsumptionRecord(
                metadata=cls.cm_ng,
                start=datetime(2011, 1, 1, tzinfo=pytz.UTC) + timedelta(days=i),
                value=value,
                estimated=False,
            ))

        for i in range(0, 6000):
            if i % 4 == 0:
                value = np.nan
            else:
                value = 1
            records.append(models.ConsumptionRecord(
                metadata=cls.cm_e,
                start=datetime(2011, 12, 1, tzinfo=pytz.UTC) + timedelta(seconds=i*900),
                value=value,
                estimated=False,
            ))

        models.ConsumptionRecord.objects.bulk_create(records)

        cls.project2 = models.Project.objects.create(
            project_owner=cls.project_owner,
            project_id="DEF",
            baseline_period_start=None,
            baseline_period_end=datetime(2012, 1, 1, tzinfo=pytz.UTC),
            reporting_period_start=datetime(2012, 1, 2, tzinfo=pytz.UTC),
            reporting_period_end=None,
            zipcode="91104",
            weather_station="722880",
            latitude=0,
            longitude=0,
        )

        cls.cm_ng = models.ConsumptionMetadata.objects.create(
            project=cls.project2,
            interpretation="NG_C_S",
            unit="THM",
        )

        cls.cm_e = models.ConsumptionMetadata.objects.create(
            project=cls.project2,
            interpretation="E_C_S",
            unit="KWH",
        )

        records = []

        for i in range(0, 700, 30):
            if i % 120 == 0:
                value = np.nan
            else:
                value = 1.0
            records.append(models.ConsumptionRecord(
                metadata=cls.cm_ng,
                start=datetime(2011, 1, 1, tzinfo=pytz.UTC) + timedelta(days=i),
                value=value,
                estimated=False,
            ))

        for i in range(0, 6000):
            if i % 4 == 0:
                value = np.nan
            else:
                value = 1
            records.append(models.ConsumptionRecord(
                metadata=cls.cm_e,
                start=datetime(2011, 12, 1, tzinfo=pytz.UTC) + timedelta(seconds=i*900),
                value=value,
                estimated=False,
            ))

        models.ConsumptionRecord.objects.bulk_create(records)

        cls.app = ApplicationModel.objects.create(
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
