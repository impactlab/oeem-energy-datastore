from .shared import OAuthTestCase

import json

class ProjectRunAPITestCase(OAuthTestCase):

    def setUp(self):
        super(ProjectRunAPITestCase, self).setUp()

    def test_project_run_create_read(self):

        data = {
            'project': self.project.pk
        }

        response = self.post('/api/v1/project_runs/', data)
        assert response.status_code == 201

        # TODO: test unauth'd project id

        # TODO: test invalid project id