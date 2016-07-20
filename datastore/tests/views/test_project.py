from datetime import datetime, timedelta

import pytz
import numpy as np

from .shared import OAuthTestCase
from datastore import models


class ProjectAPITestCase(OAuthTestCase):

    @classmethod
    def setUpTestData(cls):
        super(ProjectAPITestCase, cls).setUpTestData()

        cls.project_data = {
            "project_owner": cls.project_owner.id,
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

        cls.empty_project = models.Project.objects.create(
            project_owner=cls.user.projectowner,
            project_id="PROJECTID_1",
        )

        cls.complete_project = models.Project.objects.create(
            project_owner=cls.user.projectowner,
            project_id="PROJECTID_2",
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
            project=cls.complete_project,
            interpretation="NG_C_S",
            unit="THM",
        )

        cls.cm_e = models.ConsumptionMetadata.objects.create(
            project=cls.complete_project,
            interpretation="E_C_S",
            unit="KWH",
        )

        records = []

        for i in range(0, 700, 30):
            if i % 120 == 0:
                value = np.nan
            else:
                value = 1.0
            start = datetime(2011, 1, 1, tzinfo=pytz.UTC) + timedelta(days=i)
            records.append(models.ConsumptionRecord(
                metadata=cls.cm_ng,
                start=start,
                value=value,
                estimated=False,
            ))

        for i in range(0, 6000):
            if i % 4 == 0:
                value = np.nan
            else:
                value = 1
            start = (
                datetime(2011, 12, 1, tzinfo=pytz.UTC) +
                timedelta(seconds=i*900)
            )
            records.append(models.ConsumptionRecord(
                metadata=cls.cm_e,
                start=start,
                value=value,
                estimated=False,
            ))

        models.ConsumptionRecord.objects.bulk_create(records)

    def test_project_create_read(self):

        response = self.post('/api/v1/projects/', self.project_data)
        assert response.status_code == 201

        assert isinstance(response.data['id'], int)

        assert response.data['project_owner'] == self.project_owner.id
        assert response.data['project_id'] == "PROJECT_ID"
        assert response.data['baseline_period_start'] == "2014-01-01T00:00:00Z"
        assert response.data['baseline_period_end'] == "2014-01-01T00:00:00Z"
        assert response.data['reporting_period_start'] == \
            "2014-01-01T00:00:00Z"
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
        assert response.data['reporting_period_start'] == \
            "2014-01-01T00:00:00Z"
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
        assert response.data[0]['baseline_period_start'] is None
        assert response.data[0]['baseline_period_end'] == \
            '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_start'] == \
            '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_end'] is None
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
        assert response.data[0]['baseline_period_start'] is None
        assert response.data[0]['baseline_period_end'] == \
            '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_start'] == \
            '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_end'] is None
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
        assert response.data[0]['baseline_period_start'] is None
        assert response.data[0]['baseline_period_end'] == \
            '2014-01-01T00:00:00Z'
        assert response.data[0]['reporting_period_start'] == \
            '2014-01-02T00:00:00Z'
        assert response.data[0]['reporting_period_end'] is None
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

        response.data[0]['message'] == \
            "could not convert string to float: 'NOT A NUMBER'"
        response.data[0]['project_id'] == 'PROJECT_ID'
        response.data[0]['status'] == 'error - bad field value - update'

    def test_project_read_no_query_params(self):
        data = self.get(
            '/api/v1/projects/{}/'
            .format(self.complete_project.pk)
        ).json()

        fields = set([
            'id',
            'project_owner',
            'project_id',
            'baseline_period_start',
            'baseline_period_end',
            'reporting_period_start',
            'reporting_period_end',
            'zipcode',
            'weather_station',
            'latitude',
            'longitude',
        ])

        assert fields == set(data.keys())

    def test_project_read_with_attributes(self):
        data = self.get(
            '/api/v1/projects/{}/?with_attributes=True'
            .format(self.complete_project.pk)
        ).json()

        fields = set([
            'id',
            'project_owner',
            'project_id',
            'baseline_period_start',
            'baseline_period_end',
            'reporting_period_start',
            'reporting_period_end',
            'zipcode',
            'weather_station',
            'latitude',
            'longitude',
            'attributes',
        ])

        assert fields == set(data.keys())
