from .shared import OAuthTestCase

import json

class ProjectAPITestCase(OAuthTestCase):

    def test_project_create_read(self):
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

        response = self.post('/api/v1/projects/', project_data)
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
