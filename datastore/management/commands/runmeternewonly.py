from django.core.management.base import BaseCommand
from datastore.models import Project

class Command(BaseCommand):
    help = 'Runs the meter for all projects without.'

    def handle(self, *args, **options):

        for project in Project.objects.all():
            if project.meterrun_set.all() == []:
                print("Running meter for {}".format(project))
                project.run_meter()
            else:
                print("Skipping meter for {}".format(project))
