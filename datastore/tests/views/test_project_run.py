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
        # Test the default for meter_type
        assert response.data['meter_class'] == 'DefaultResidentialMeter'


        # Test failing meter_class validation
        data = {
            'project': self.project2.pk,
            'meter_class': 'foo'
        }
        response = self.post('/api/v1/project_runs/', data)
        assert response.status_code == 400


        # Test filtered retrieval for the first project
        data = {
            'projects': self.project.pk
        }
        response = self.get('/api/v1/project_runs/', data=data)
        assert len(response.data) == 1
        project_run = response.data[0]

        assert project_run['project'] == self.project.pk

        assert list(project_run.keys()) == [
            "id",
            "project",
            "meter_class",
            "meter_settings",
            "start_date",
            "end_date",
            "n_days",
            "status",
            "traceback",
            "added",
            "updated",
        ]

    def test_project_run_status_success(self):

        # bad meter type
        data = {
            'project': self.project.pk,
            'meter_type': 'residential',
        }
        response = self.post('/api/v1/project_runs/', data)
        project_run = response.data

        assert project_run['status'] == 'PENDING'

        response = self.get('/api/v1/project_runs/{}/'.format(project_run['id']))
        project_run = response.data

        assert project_run['status'] == 'SUCCESS'
        assert project_run['traceback'] is None

    def test_project_run_bad_project_id(self):

        # bad project id
        data = {
            'project': 99999999,
        }
        response = self.post('/api/v1/project_runs/', data)
        project_run = response.data
        assert 'Invalid pk "99999999"' in project_run['project'][0]
