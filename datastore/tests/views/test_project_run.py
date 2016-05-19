from .shared import OAuthTestCase

import json

class ProjectRunAPITestCase(OAuthTestCase):

    def setUp(self):
        super(ProjectRunAPITestCase, self).setUp()

    def test_project_run_create_read(self):

        # Create a project run for the first project
        data = {
            'project': self.project.pk
        }
        response = self.post('/api/v1/project_runs/', data)
        assert response.status_code == 201

        # Now the second project
        data = {
            'project': self.project2.pk
        }
        response = self.post('/api/v1/project_runs/', data)
        assert response.status_code == 201


        # Test filtered retrieval for the first project
        data = {
            'projects': self.project.pk
        }
        response = self.get('/api/v1/project_runs/', data=data)
        assert len(response.data) == 1
        project_run = response.data[0]
        assert project_run['project'] == 1

        assert project_run['status'] == 'SUCCESS'

        # TODO: test unauth'd project id

        # TODO: test invalid project id
