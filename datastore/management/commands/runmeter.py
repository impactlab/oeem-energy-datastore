from django.core.management.base import BaseCommand
from datastore.models import Project

class Command(BaseCommand):
    help = 'Runs the meter for all projects.'

    def handle(self, *args, **options):

        for project in Project.objects.all():
            if project.project_id != 'CF-00000203':
                continue
            print("Running meter for {}".format(project))
            project.run_meter()
