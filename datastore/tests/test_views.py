from django.test import Client, TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta, make_aware

from ..models import ProjectOwner
from ..models import ProjectBlock
from ..models import Project
from ..models import MeterRun
from ..models import ConsumptionMetadata
from ..models import ConsumptionRecord

from oauth2_provider.models import AccessToken
from oauth2_provider.models import get_application_model

from eemeter.consumption import ConsumptionData as EEMeterConsumptionData
from eemeter.project import Project as EEMeterProject
from eemeter.examples import get_example_project
from eemeter.evaluation import Period

import json
from datetime import datetime
from numpy.testing import assert_allclose

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
        self.user = User.objects.create_user("user", "test@user.com", "123456")
        self.project_owner = ProjectOwner(user=self.user)
        self.project_owner.save()
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

class ConsumptionMetadataAPITestCase(OAuthTestCase):

    def test_consumption_metatdata_bad_token(self):
        """
        Tests the oauth token againist the consumption
        API. Makes sure that that section of the
        API requires auth.
        """
        auth_headers = {"Authorization": "Bearer " + "badtoken" }
        response = self.client.get('/datastore/consumption/', **auth_headers)
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
        response = self.client.get('/datastore/consumption/', **auth_headers)
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
                "records": [{
                    "start": "2014-01-01T00:00:00+00:00",
                    "value": 0,
                    "estimated": False,
                }],
                }

        data = json.dumps(consumption_data)
        response = self.client.post('/datastore/consumption/', data, content_type="application/json", **auth_headers)

        assert response.status_code == 201

        assert isinstance(response.data['id'], int)
        assert response.data['energy_unit'] == 'KWH'
        assert response.data['fuel_type'] == 'E'
        assert response.data['project'] == None
        assert len(response.data['records']) == 1

        consumption_metadata_id = response.data['id']
        response = self.client.get('/datastore/consumption/{}/'.format(consumption_metadata_id), **auth_headers)

        assert response.status_code == 200

        assert response.data['id'] == consumption_metadata_id
        assert response.data['energy_unit'] == 'KWH'
        assert response.data['fuel_type'] == 'E'
        assert response.data['project'] == None

        assert len(response.data['records']) == 1
        assert response.data['records'][0]['start'] == "2014-01-01T00:00:00Z"
        assert response.data['records'][0]['value'] == 0
        assert response.data['records'][0]['estimated'] == False

class ProjectAPITestCase(OAuthTestCase):

    def test_project_create_read(self):
        """
        Tests if a user with proper auth can
        post and read back data for a project
        endpoint under test: /datastore/project
        """
        auth_headers = { "Authorization": "Bearer " + "tokstr" }

        project_data = {
                "project_owner": self.project_owner.id,
                "project_id": "PROJECT_ID",
                "baseline_period_start": "2014-01-01T00:00:00+00:00",
                "baseline_period_end": "2014-01-01T00:00:00+00:00",
                "reporting_period_start": "2014-01-01T00:00:00+00:00",
                "reporting_period_end": "2014-01-01T00:00:00+00:00",
                "zipcode": "ZIPCODE",
                "weather_station": "STATION",
                "latitude": 0.0,
                "longitude": 0.0,
                }

        data = json.dumps(project_data)
        response = self.client.post('/datastore/project/', data, content_type="application/json", **auth_headers)
        assert response.status_code == 201

        assert isinstance(response.data['id'], int)

        assert response.data['project_owner'] == self.project_owner.id
        assert response.data['project_id'] == "PROJECT_ID"
        assert response.data['baseline_period_start'] == "2014-01-01T00:00:00Z"
        assert response.data['baseline_period_end'] == "2014-01-01T00:00:00Z"
        assert response.data['reporting_period_start'] == "2014-01-01T00:00:00Z"
        assert response.data['reporting_period_end'] == "2014-01-01T00:00:00Z"
        assert response.data['zipcode'] == "ZIPCODE"
        assert response.data['weather_station'] == "STATION"
        assert response.data['latitude'] == 0.0
        assert response.data['longitude'] == 0.0

        project_id = response.data['id']
        response = self.client.get('/datastore/project/{}/'.format(project_id), **auth_headers)
        assert response.status_code == 200

        assert response.data['id'] == project_id

        assert response.data['project_owner'] == self.project_owner.id
        assert response.data['project_id'] == "PROJECT_ID"
        assert response.data['baseline_period_start'] == "2014-01-01T00:00:00Z"
        assert response.data['baseline_period_end'] == "2014-01-01T00:00:00Z"
        assert response.data['reporting_period_start'] == "2014-01-01T00:00:00Z"
        assert response.data['reporting_period_end'] == "2014-01-01T00:00:00Z"
        assert response.data['zipcode'] == "ZIPCODE"
        assert response.data['weather_station'] == "STATION"
        assert response.data['latitude'] == 0.0
        assert response.data['longitude'] == 0.0
        assert response.data['recent_meter_runs'] == []

class MeterRunAPITestCase(OAuthTestCase):

    def setUp(self):
        """
        Setup methods for a eemeter run storage
        engine.
        """
        super(MeterRunAPITestCase,self).setUp()

        zipcode = "91104"
        project = get_example_project(zipcode)

        self.project = Project(
                project_owner=self.project_owner,
                project_id="TEST_PROJECT",
                baseline_period_start=project.baseline_period.start,
                baseline_period_end=project.baseline_period.end,
                reporting_period_start=project.reporting_period.start,
                reporting_period_end=project.reporting_period.end,
                zipcode=None,
                weather_station=project.location.station,
                latitude=None,
                longitude=None,
                )
        self.project.save()

        fuel_types = {"electricity": "E", "natural_gas": "NG"}
        energy_units = {"kWh": "KWH", "therm": "THM"}

        self.consumption_metadatas = []
        for consumption_data in project.consumption:
            consumption_metadata = ConsumptionMetadata(
                    project=self.project,
                    fuel_type=fuel_types[consumption_data.fuel_type],
                    energy_unit=energy_units[consumption_data.unit_name])
            consumption_metadata.save()
            self.consumption_metadatas.append(consumption_metadata)

            for record in consumption_data.records(record_type="arbitrary_start"):
                record = ConsumptionRecord(metadata=consumption_metadata,
                    start=record["start"].isoformat(),
                    value=record["value"],
                    estimated=False)
                record.save()

        ## Attempt to run the meter
        self.project.run_meter(start_date=make_aware(datetime(2011,1,1)), end_date=make_aware(datetime(2015,1,1)))
        self.meter_runs = [MeterRun.objects.get(consumption_metadata=cm) for cm in self.consumption_metadatas]
        assert len(self.meter_runs) == 2

    def test_meter_run_read(self):
        """
        Tests reading a meter run data.
        endpoint: /datastore/meter_run/{id}
        """
        auth_headers = { "Authorization": "Bearer " + "tokstr" }

        for meter_run, consumption_metadata in zip(self.meter_runs,self.consumption_metadatas):

            response = self.client.get('/datastore/meter_run/{}/'.format(meter_run.id), **auth_headers)
            assert response.status_code == 200
            assert response.data["project"] == self.project.id
            assert response.data["consumption_metadata"] == consumption_metadata.id

            model_parameters_baseline = json.loads(response.data["model_parameter_json_baseline"])
            model_parameters_reporting = json.loads(response.data["model_parameter_json_reporting"])

            assert type(model_parameters_baseline) == dict
            assert type(model_parameters_reporting) == dict

            assert len(response.data["serialization"]) > 7000

            assert len(response.data["dailyusagebaseline_set"]) == 1461
            assert len(response.data["dailyusagereporting_set"]) == 1461

            assert response.data["meter_type"] == "DFLT_RES_E" or \
                    response.data["meter_type"] == "DFLT_RES_NG"

            assert type(response.data["annual_usage_baseline"]) == float
            assert type(response.data["annual_usage_reporting"]) == float
            assert type(response.data["gross_savings"]) == float
            assert type(response.data["annual_savings"]) == float
            assert type(response.data["cvrmse_baseline"]) == float
            assert type(response.data["cvrmse_reporting"]) == float

class ProjectBlockAPITestCase(OAuthTestCase):

    def setUp(self):
        """
        Setup methods for a eemeter run storage
        engine.
        """
        super(ProjectBlockAPITestCase,self).setUp()

        self.project = Project(
                project_owner=self.project_owner,
                project_id="TEST_PROJECT",
                baseline_period_start=now(),
                baseline_period_end=now(),
                reporting_period_start=now(),
                reporting_period_end=now(),
                zipcode=None,
                weather_station=None,
                latitude=None,
                longitude=None,
                )
        self.project.save()
        self.project_block = ProjectBlock(name="NAME", project_owner=self.project_owner)
        self.project_block.save()
        self.project_block.project.add(self.project)
        self.project_block.save()

    def test_project_block_read(self):

        auth_headers = { "Authorization": "Bearer " + "tokstr" }

        response = self.client.get('/datastore/project_block/{}/'.format(self.project_block.id), **auth_headers)
        assert response.status_code == 200
        assert response.data['project'][0] == self.project.id
        assert response.data['project_owner'] == self.project_owner.id
        assert response.data['id'] == self.project_block.id
        assert response.data['name'] == 'NAME'
