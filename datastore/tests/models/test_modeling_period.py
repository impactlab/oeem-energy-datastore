from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from datetime import datetime

import pytz
import pytest
import numpy as np

from datastore.models import ModelingPeriod, Project, ProjectResult


class ModelingPeriodTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'john', 'lennon@thebeatles.com', 'johnpassword')

        self.project = Project.objects.create(
            project_id="ABCDE",
            project_owner=self.user.projectowner)

        self.project_result = ProjectResult.objects.create(
            project=self.project,
            eemeter_version="VERSION")

    def test_blank_dates_not_ok(self):
        with pytest.raises(ValidationError):
            mp = ModelingPeriod.objects.create(
                project_result=self.project_result,
                interpretation="BASELINE",
                start_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
            )
            mp.full_clean()

        with pytest.raises(ValidationError):
            mp = ModelingPeriod.objects.create(
                project_result=self.project_result,
                interpretation="REPORTING",
                end_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
            )
            mp.full_clean()

    def test_blank_dates_ok(self):
        mp = ModelingPeriod.objects.create(
            project_result=self.project_result,
            interpretation="BASELINE",
            end_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
        )
        mp.full_clean()

        mp = ModelingPeriod.objects.create(
            project_result=self.project_result,
            interpretation="REPORTING",
            start_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
        )
        mp.full_clean()

    def test_basic_usage(self):
        mp = ModelingPeriod.objects.create(
            project_result=self.project_result,
            interpretation="BASELINE",
            end_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
        )

        assert np.isinf(mp.n_days())

        mp.start_date = datetime(2011, 12, 31, tzinfo=pytz.UTC)
        mp.save()

        assert mp.n_days() == 1
