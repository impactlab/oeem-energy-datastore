from .shared import OAuthTestCase

from datastore import models

class ConsumptionRecordAPITestCase(OAuthTestCase):

    def setUp(self):
        """
        Setup methods for a eemeter run storage
        engine.
        """
        super(ConsumptionRecordAPITestCase,self).setUp()

        self.consumption_metadata = models.ConsumptionMetadata(
            fuel_type="E",
            energy_unit="KWH",
        )
        self.consumption_metadata.save()

    def test_consumption_record_sync(self):

        response = self.post('/api/v1/consumption_metadatas/sync/', [{
            "project_project_id": "ABC",
            "energy_unit": "KWH",
            "fuel_type": "E"
        }])

        assert response.data[0]['status'] == 'created'
        cm_id = response.data[0]['id']

        response = self.post('/api/v1/consumption_records/sync/', [{
            "project_id": "ABC",
            "energy_unit": "KWH",
            "fuel_type": "E",
            "start": "2014-01-01T00:00:00+00:00",
            "value": 1.0,
            "estimated": True
        }, {
            "project_id": "ABC",
            "energy_unit": "KWH",
            "fuel_type": "E",
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
            "energy_unit": "KWH",
            "fuel_type": "E"
        }, {
            "project_project_id": "DEF",
            "energy_unit": "KWH",
            "fuel_type": "E"
        }])

        assert response.data[0]['status'] == 'created'
        cm_id = response.data[0]['id']
        cm_id2 = response.data[1]['id']

        # Make sure the records don't already exist
        def get_test_record_by_start(start, cm_id=cm_id):
            return models.ConsumptionRecord.objects.filter(start=start, metadata_id=cm_id).first()
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

        # Test updating
        response = self.post('/api/v1/consumption_records/sync2/', [{
            "metadata_id": cm_id,
            "start": start_a,
            "value": 3.0,
            "estimated": True
        }])

        a = get_test_record_by_start(start_a)
        assert a.value == 3.0

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


    def test_consumption_record_create_read(self):
        data = [{
            "start": "2014-01-01T00:00:00+00:00",
            "value": 0.0,
            "estimated": False,
            "metadata": self.consumption_metadata.pk,
        }]

        response = self.post('/api/v1/consumption_records/', data)

        assert response.status_code == 201

        assert isinstance(response.data[0]['id'], int)
        assert response.data[0]['start'] == '2014-01-01T00:00:00Z'
        assert response.data[0]['value'] == 0.0
        assert response.data[0]['estimated'] == False
        assert response.data[0]['metadata'] == self.consumption_metadata.pk

        consumption_record_id = response.data[0]['id']
        response = self.get('/api/v1/consumption_records/{}/'.format(consumption_record_id))

        assert response.status_code == 200

        assert isinstance(response.data['id'], int)
        assert response.data['start'] == '2014-01-01T00:00:00Z'
        assert response.data['value'] == 0.0
        assert response.data['estimated'] == False
        assert response.data['metadata'] == self.consumption_metadata.pk

