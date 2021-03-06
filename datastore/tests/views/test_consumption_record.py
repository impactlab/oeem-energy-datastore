from .shared import OAuthTestCase

from datastore import models


class ConsumptionRecordAPITestCase(OAuthTestCase):

    def setUp(self):
        super(ConsumptionRecordAPITestCase, self).setUp()

    def test_consumption_record_sync(self):

        response = self.post('/api/v1/consumption_metadatas/sync/', [{
            "project_project_id": "ABC",
            "unit": "KWH",
            "interpretation": "E_C_S",
            "label": "first-trace"
        }])

        cm_id = response.data[0]['id']

        response = self.post('/api/v1/consumption_records/sync/', [{
            "project_id": "ABC",
            "unit": "KWH",
            "interpretation": "E_C_S",
            "label": "first-trace",
            "start": "2014-01-01T00:00:00+00:00",
            "value": 1.0,
            "estimated": True
        }, {
            "project_id": "ABC",
            "unit": "KWH",
            "interpretation": "E_C_S",
            "label": "first-trace",
            "start": "2014-01-01T01:00:00+00:00",
            "value": 2.0,
            "estimated": True
        }])

        assert response.data[0]['status'] == 'created'
        assert response.data[0]['metadata'] == cm_id
        assert response.data[1]['metadata'] == cm_id

    def test_consumption_record_sync2(self):

        # Create a two metadata objects
        response = self.post('/api/v1/consumption_metadatas/sync/', [{
            "project_project_id": "ABC",
            "unit": "KWH",
            "interpretation": "E_C_S",
            "label": "first-trace"
        }, {
            "project_project_id": "DEF",
            "unit": "KWH",
            "interpretation": "E_C_S",
            "label": "first-trace"
        }])

        cm_id = response.data[0]['id']
        cm_id2 = response.data[1]['id']

        # Make sure the records don't already exist
        def get_test_record_by_start(start, cm_id=cm_id):
            return models.ConsumptionRecord.objects.filter(
                start=start, metadata_id=cm_id).first()
        start_a = "2014-01-01T00:00:00+00:00"
        start_b = "2014-01-01T01:00:00+00:00"
        a = get_test_record_by_start(start_a)
        b = get_test_record_by_start(start_b)
        assert a is None
        assert b is None

        response = self.post('/api/v1/consumption_records/sync2/', [{
            "metadata_id": cm_id,
            "start": start_a,
            "value": 1.0,
            "estimated": True
        }, {
            "metadata_id": cm_id,
            "start": start_b,
            "value": 2.0,
            "estimated": True
        }])

        # Check that the two records were created
        a = get_test_record_by_start(start_a)
        b = get_test_record_by_start(start_b)
        assert a is not None
        assert b is not None

        # Test updating and adding
        start_c = "2014-01-01T02:00:00+00:00"

        response = self.post('/api/v1/consumption_records/sync2/', [{
            "metadata_id": cm_id,
            "start": start_a,
            "value": 3.0,
            "estimated": False
        }, {
            "metadata_id": cm_id,
            "start": start_c,
            "value": 4.0,
            "estimated": False
        }])

        a = get_test_record_by_start(start_a)
        assert a.value == 3.0

        c = get_test_record_by_start(start_c)
        assert c.value == 4.0
        assert c.estimated is False

        # Test metadata_id keys properly
        response = self.post('/api/v1/consumption_records/sync2/', [{
            "metadata_id": cm_id2,
            "start": start_a,
            "value": 4.0,
            "estimated": True
        }])

        c = get_test_record_by_start(start_a, cm_id=cm_id2)
        assert c is not None
        assert c.value == 4.0

        # Sending a dict instead of a list should be handled gracefully
        response = self.post('/api/v1/consumption_records/sync2/', {
            "start": start_a,
            "metadata_id": cm_id,
            "estimated": False,
            "value": 1.0
        })
        assert response.status_code == 200

        # A null `value` should be supported
        response = self.post('/api/v1/consumption_records/sync2/', [{
            "start": start_a,
            "metadata_id": cm_id,
            "estimated": False,
            "value": None
        }])
        assert response.status_code == 200
        a = get_test_record_by_start(start_a)
        assert a is not None
        assert a.value is None

        # Test some invalid records

        # Missing field `start` should error out
        response = self.post('/api/v1/consumption_records/sync2/', [{
            "metadata_id": cm_id,
            "estimated": False,
            "value": 1.0
        }])
        assert response.status_code == 400
        assert response.data['status'] == 'error'

        # Invalid `value` should return an error status
        response = self.post('/api/v1/consumption_records/sync2/', [{
            "metadata_id": cm_id,
            "start": start_a,
            "estimated": False,
            "value": "foo"
        }])
        assert response.status_code == 400
        assert response.data['status'] == 'error'

    def test_consumption_record_create_read(self):

        response = self.post('/api/v1/consumption_metadatas/sync/', [{
            "project_project_id": "ABC",
            "unit": "KWH",
            "interpretation": "E_C_S",
            "label": "first-trace"
        }])
        cm_id = response.data[0]['id']

        data = [{
            "start": "2014-01-01T00:00:00+00:00",
            "value": 0.0,
            "estimated": False,
            "metadata": cm_id,
        }]

        response = self.post('/api/v1/consumption_records/', data)

        assert response.status_code == 201

        assert isinstance(response.data[0]['id'], int)
        assert response.data[0]['start'] == '2014-01-01T00:00:00Z'
        assert response.data[0]['value'] == 0.0
        assert response.data[0]['estimated'] is False
        assert response.data[0]['metadata'] == cm_id

        consumption_record_id = response.data[0]['id']
        response = self.get(
            '/api/v1/consumption_records/{}/'.format(consumption_record_id))

        assert response.status_code == 200

        assert isinstance(response.data['id'], int)
        assert response.data['start'] == '2014-01-01T00:00:00Z'
        assert response.data['value'] == 0.0
        assert response.data['estimated'] is False
        assert response.data['metadata'] == cm_id
