from .shared import OAuthTestCase

import json

class MeterRunJobAPITestCase(OAuthTestCase):

    def setUp(self):
        super(MeterRunJobAPITestCase, self).setUp()

    def test_meter_run_job_create_read(self):

        data = {
            'project': self.project.pk,
        }

        response = self.post('/api/v1/meter_run_jobs/', data)
        assert response.status_code == 201

        # TODO: test unauth'd project id

        # TODO: test invalid project id