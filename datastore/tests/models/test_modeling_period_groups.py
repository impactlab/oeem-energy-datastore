from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from datetime import datetime

import pytz
import pytest

from datastore.models import (
    ModelingPeriod,
    ModelingPeriodGroup,
    Project,
    ProjectResult
)


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

    def test_no_gap(self):
        bp = ModelingPeriod.objects.create(
            project_result=self.project_result,
            interpretation="BASELINE",
            end_date=datetime(2012, 2, 1, tzinfo=pytz.UTC),
        )
        rp = ModelingPeriod.objects.create(
            project_result=self.project_result,
            interpretation="REPORTING",
            start_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
        )

        # periods overlap
        with pytest.raises(ValidationError):
            mpg = ModelingPeriodGroup.objects.create(
                project_result=self.project_result,
                baseline_period=bp,
                reporting_period=rp,
            )
            mpg.full_clean()

    def test_incorrect_types(self):
        bp = ModelingPeriod.objects.create(
            project_result=self.project_result,
            interpretation="BASELINE",
            end_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
        )
        rp = ModelingPeriod.objects.create(
            project_result=self.project_result,
            interpretation="REPORTING",
            start_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
        )

        # reporting instead of baseline
        with pytest.raises(ValidationError):
            mpg = ModelingPeriodGroup.objects.create(
                project_result=self.project_result,
                baseline_period=rp,
                reporting_period=rp,
            )
            mpg.full_clean()

        # baseline instead of reporting
        with pytest.raises(ValidationError):
            mpg = ModelingPeriodGroup.objects.create(
                project_result=self.project_result,
                baseline_period=bp,
                reporting_period=bp,
            )
            mpg.full_clean()

    def test_ok(self):
        bp = ModelingPeriod.objects.create(
            project_result=self.project_result,
            interpretation="BASELINE",
            end_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
        )
        rp = ModelingPeriod.objects.create(
            project_result=self.project_result,
            interpretation="REPORTING",
            start_date=datetime(2012, 1, 1, tzinfo=pytz.UTC),
        )

        mpg = ModelingPeriodGroup.objects.create(
            project_result=self.project_result,
            baseline_period=bp,
            reporting_period=rp,
        )
        mpg.full_clean()

        assert mpg.n_gap_days() == 0
