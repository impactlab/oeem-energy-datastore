from django.core.management.base import BaseCommand
from datastore.models import Project


class Command(BaseCommand):
    help = 'Runs the meter for all projects without.'

    def handle(self, *args, **options):

        for project in Project.objects.all():
            if len(project.meterrun_set.all()) == 0:
                print("Running meter for {}".format(project))
                project.run_meter()
            else:
                print("Skipping meter for {}".format(project))
