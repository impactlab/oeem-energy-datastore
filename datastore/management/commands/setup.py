from django.core.management.base import BaseCommand
from datastore.models import *
from django.contrib.auth.models import User

from eemeter.consumption import ConsumptionData as EEMeterConsumptionData
from eemeter.project import Project as EEMeterProject
from eemeter.examples import get_example_project
from eemeter.evaluation import Period

from datetime import datetime

class Command(BaseCommand):
    help = "Initize the datastore with sample data and users"

    def handle(self, *args, **options):
        # create a superuser
        user = User.objects.create_superuser('demo','demo@example.com','demo-password')
        user.save()
        ## consumption data
        
        consumption_metadata = ConsumptionMetadata(fuel_type="E", energy_unit="KWH")
        consumption_metadata.save()
        record = ConsumptionRecord(
            metadata=self.consumption_metadata, start=now(), estimated=False)
        record.save()

        consumption_data = consumption_metadata.eemeter_consumption_data()

        project_owner = ProjectOwner(user=user)
        project_owner.save()

        project = get_example_project("91104")

        project = Project(
                project_owner=project_owner,
                project_id="TEST_PROJECT",
                baseline_period_start=project.baseline_period.start,
                baseline_period_end=project.baseline_period.end,
                reporting_period_start=project.reporting_period.start,
                reporting_period_end=project.reporting_period.end,
                zipcode=None,
                weather_station=None,
                latitude=None,
                longitude=None,
                )
        project.save()



