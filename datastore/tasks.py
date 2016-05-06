from __future__ import absolute_import

from celery import shared_task

from datastore.models import Project


@shared_task
def run_meter(project_run_pk):
    print "Going to run meter %s" % project_run_pk
    # project = Project.objects.get(pk=project_pk)
    # project.run_meter()
