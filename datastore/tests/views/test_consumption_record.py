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
