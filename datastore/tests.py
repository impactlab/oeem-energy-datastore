from django.test import Client, TestCase, RequestFactory
from django.contrib.auth.models import User
from .models import ProjectOwner
from .models import Project
from .models import MeterRun
from .models import ConsumptionMetadata
from .models import ConsumptionRecord
from django.utils.timezone import now, timedelta
from oauth2_provider.models import AccessToken
from oauth2_provider.models import get_application_model
import json
from datetime import datetime
from eemeter.project import Project as EEMeterProject
from eemeter.consumption import ConsumptionData as EEMeterConsumptionData
from eemeter.evaluation import Period
from eemeter.examples import get_example_project

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

class MeterRunAPITestCase(OAuthTestCase):

    def setUp(self):
        """
        Setup methods for a eemeter run storage
        engine.
        """
        super(MeterRunAPITestCase,self).setUp()

        project = get_example_project("60642")

        self.project = Project(
                project_owner=self.project_owner,
                project_id="TEST_PROJECT",
                baseline_period_start=project.baseline_period.start,
                baseline_period_end=project.baseline_period.end,
                reporting_period_start=project.reporting_period.start,
                reporting_period_end=project.reporting_period.end,
                zipcode="60642",
                weather_station=None,
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
        self.project.run_meter()
        self.meter_runs = self.project.meterrun_set.all()
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
            assert type(response.data["consumption_metadata"]) == int 
            assert response.data["model_parameter_json"] == None
            assert response.data["annual_usage_reporting"] == None
            assert response.data["annual_usage_baseline"] == None
            assert response.data["gross_savings"] == None
            assert response.data["annual_savings"] == None
            assert response.data["model_type"] == "DFLT_RES_E" or "DFLT_RES_NG" 
            assert response.data["serialization"] == None
            assert response.data["dailyusagebaseline_set"] == []
            assert response.data["dailyusagereporting_set"] == []


class ProjectTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("user", "test@user.com", "123456")
        self.project_owner = ProjectOwner(user=self.user)
        self.project_owner.save()
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

    def tearDown(self):
        self.user.delete()
        self.project_owner.delete()

    def test_project_baseline_period(self):
        period = self.project.baseline_period
        assert isinstance(period, Period)
        assert isinstance(period.start, datetime)
        assert isinstance(period.end, datetime)

    def test_project_reporting_period(self):
        period = self.project.reporting_period
        assert isinstance(period, Period)
        assert isinstance(period.start, datetime)
        assert isinstance(period.end, datetime)

    def test_project_lat_lng(self):
        assert self.project.lat_lng is None
        self.project.latitude = 41.8
        self.project.longitude = -87.6
        assert self.project.lat_lng is not None

    def test_project_eemeter_project_with_zipcode(self):
        self.project.zipcode = "91104"
        project, cm_ids = self.project.eemeter_project()
        assert isinstance(project, EEMeterProject)
        assert cm_ids == []

    def test_project_eemeter_project_with_lat_lng(self):
        self.project.latitude = 41.8
        self.project.longitude = -87.6
        project, cm_ids= self.project.eemeter_project()
        assert isinstance(project, EEMeterProject)
        assert cm_ids == []


    def test_project_eemeter_project_with_station(self):
        self.project.weather_station = "722880"
        project, cm_ids = self.project.eemeter_project()
        assert isinstance(project, EEMeterProject)
        assert cm_ids == []

    def test_project_run_meter(self):
        assert len(self.project.meterrun_set.all()) == 0

        # set up project
        self.project.weather_station = "722880"
        consumption_metadata = ConsumptionMetadata(project=self.project,
                fuel_type="E", energy_unit="KWH")
        consumption_metadata.save()

        # run meter
        self.project.run_meter()

        assert len(self.project.meterrun_set.all()) == 1


class ConsumptionTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("user", "test@user.com", "123456")
        self.consumption_metadata = ConsumptionMetadata(fuel_type="E", energy_unit="KWH")
        self.consumption_metadata.save()
        self.record = ConsumptionRecord(
            metadata=self.consumption_metadata, start=now(), estimated=False)
        self.record.save()

    def tearDown(self):
        self.user.delete()

    def test_consumption_eemeter_consumption_data(self):
        consumption_data = self.consumption_metadata.eemeter_consumption_data()
        assert isinstance(consumption_data, EEMeterConsumptionData)

    def test_consumption_eemeter_record(self):
        record = self.record.eemeter_record()
        assert isinstance(record, dict)
        assert record["start"] == self.record.start
        assert record["value"] == self.record.value
        assert record["estimated"] == self.record.estimated
        assert len(record) == 3
