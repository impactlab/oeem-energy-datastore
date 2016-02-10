from django.core.management.base import BaseCommand
from datastore.models import ProjectBlock

class Command(BaseCommand):
    help = 'Runs the meter for all projects in a particular block.'

    def add_arguments(self, parser):
        parser.add_argument('block_id', type=int)

    def handle(self, *args, **options):

        project_block = ProjectBlock.objects.get(id=options["block_id"])

        projects = project_block.projects.all()

        print("Running meter for {}".format(project_block, len(projects)))

        for project in projects:
            print("Running meter for {}".format(project))
            project.run_meter()

        print("Computing project block summary timeseries.")
        project_block.compute_summary_timeseries()
