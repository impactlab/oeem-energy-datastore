from .shared import OAuthTestCase

import json

class ProjectAPITestCase(OAuthTestCase):

    def setUp(self):
        super(ProjectAPITestCase, self).setUp()

        self.project_data = {
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

    def test_project_create_read(self):

        response = self.post('/api/v1/projects/', self.project_data)
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
        response = self.get('/api/v1/projects/{}/'.format(project_id))
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

    def test_project_sync_missing_field(self):

        # missing data
        response = self.post('/api/v1/projects/sync/', [{
            "project_owner": self.project_owner.id,
            "project_id": "PROJECT_ID",
            "baseline_period_start": "2014-01-01T00:00:00+00:00",
            "baseline_period_end": "2014-01-01T00:00:00+00:00",
            "reporting_period_start": "2014-01-01T00:00:00+00:00",
            "reporting_period_end": "2014-01-01T00:00:00+00:00",
            "weather_station": "STATION",
            "latitude": 0.0,
            "longitude": 0.0,
        }])

        assert response.data == [{
            'project_id': 'PROJECT_ID',
            'message': "'project_owner_id'",
            'status': 'error - missing field'
        }]

    def test_project_sync(self):

        # Original record
        response = self.post('/api/v1/projects/sync/', [{
            "project_owner_id": self.project_owner.id,
            "project_id": "PROJECT_ID",
            "baseline_period_start": "2014-01-01T00:00:00+00:00",
            "baseline_period_end": "2014-01-01T00:00:00+00:00",
            "reporting_period_start": "2014-01-01T00:00:00+00:00",
            "reporting_period_end": "2014-01-01T00:00:00+00:00",
            "zipcode": "ZIPCODE",
            "weather_station": "STATION",
            "latitude": 0.0,
            "longitude": 0.0,
        }])

        assert response.data[0]['project_owner'] == self.project_owner.id
        assert response.data[0]['project_id'] == 'PROJECT_ID'
        assert response.data[0]['baseline_period_start'] == None
        assert response.data[0]['baseline_period_end'] == '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_start'] == '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_end'] == None
        assert response.data[0]['weather_station'] == 'STATION'
        assert response.data[0]['zipcode'] == 'ZIPCODE'
        assert response.data[0]['latitude'] == 0.0
        assert response.data[0]['longitude'] == 0.0
        assert response.data[0]['status'] == 'created'
        assert isinstance(response.data[0]['id'], int)

        # unchanged, same record
        response = self.post('/api/v1/projects/sync/', [{
            "project_owner_id": self.project_owner.id,
            "project_id": "PROJECT_ID",
            "baseline_period_start": "2014-01-01T00:00:00+00:00",
            "baseline_period_end": "2014-01-01T00:00:00+00:00",
            "reporting_period_start": "2014-01-01T00:00:00+00:00",
            "reporting_period_end": "2014-01-01T00:00:00+00:00",
            "zipcode": "ZIPCODE",
            "weather_station": "STATION",
            "latitude": 0.0,
            "longitude": 0.0,
        }])

        assert response.data[0]['project_owner'] == self.project_owner.id
        assert response.data[0]['project_id'] == 'PROJECT_ID'
        assert response.data[0]['baseline_period_start'] == None
        assert response.data[0]['baseline_period_end'] == '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_start'] == '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_end'] == None
        assert response.data[0]['weather_station'] == 'STATION'
        assert response.data[0]['zipcode'] == 'ZIPCODE'
        assert response.data[0]['latitude'] == 0.0
        assert response.data[0]['longitude'] == 0.0
        assert response.data[0]['status'] == 'unchanged - same record'
        assert isinstance(response.data[0]['id'], int)

        # ignores baseline_period_start and reporting_period_end
        response = self.post('/api/v1/projects/sync/', [{
            "project_owner_id": self.project_owner.id,
            "project_id": "PROJECT_ID",
            "baseline_period_start": "2014-01-02T00:00:00+00:00",
            "baseline_period_end": "2014-01-01T00:00:00+00:00",
            "reporting_period_start": "2014-01-01T00:00:00+00:00",
            "reporting_period_end": "2014-01-02T00:00:00+00:00",
            "zipcode": "ZIPCODE",
            "weather_station": "STATION",
            "latitude": 0.0,
            "longitude": 0.0,
        }])

        assert response.data[0]['status'] == 'unchanged - same record'

        # notices change
        response = self.post('/api/v1/projects/sync/', [{
            "project_owner_id": self.project_owner.id,
            "project_id": "PROJECT_ID",
            "baseline_period_start": "2014-01-01T00:00:00+00:00",
            "baseline_period_end": "2014-01-01T00:00:00+00:00",
            "reporting_period_start": "2014-01-02T00:00:00+00:00",
            "reporting_period_end": "2014-01-02T00:00:00+00:00",
            "zipcode": "ZIPCODE",
            "weather_station": "STATION",
            "latitude": 0.0,
            "longitude": 0.0,
        }])

        assert response.data[0]['project_owner'] == self.project_owner.id
        assert response.data[0]['project_id'] == 'PROJECT_ID'
        assert response.data[0]['baseline_period_start'] == None
        assert response.data[0]['baseline_period_end'] == '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_start'] == '2014-01-02T00:00:00Z'
        assert response.data[0]['reporting_period_end'] == None
        assert response.data[0]['weather_station'] == 'STATION'
        assert response.data[0]['zipcode'] == 'ZIPCODE'
        assert response.data[0]['latitude'] == 0.0
        assert response.data[0]['longitude'] == 0.0
        assert response.data[0]['status'] == 'updated'
        assert isinstance(response.data[0]['id'], int)

        # update invalid
        response = self.post('/api/v1/projects/sync/', [{
            "project_owner_id": self.project_owner.id,
            "project_id": "PROJECT_ID",
            "baseline_period_start": None,
            "baseline_period_end": "2014-01-01T00:00:00+00:00",
            "reporting_period_start": "2014-01-01T00:00:00+00:00",
            "reporting_period_end": None,
            "zipcode": "ZIPCODE",
            "weather_station": "STATION",
            "latitude": "NOT A NUMBER",
            "longitude": 0.0,
        }])

        response.data[0]['message'] == "could not convert string to float: 'NOT A NUMBER'"
        response.data[0]['project_id'] == 'PROJECT_ID'
        response.data[0]['status'] == 'error - bad field value - update'
