from django.test import TestCase
from django.contrib.auth.models import User


class ProjectOwnerTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'john', 'lennon@thebeatles.com', 'johnpassword')

    def test_project_owner_auto_create(self):
        assert self.user.projectowner.user == self.user
