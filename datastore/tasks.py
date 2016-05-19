from __future__ import absolute_import

from celery import shared_task

from datastore.models import Project


@shared_task
def run_meter(project_run_pk):
    project = Projects.objects.get(pk=project_run_pk)
    if project:
        project.run_meter()
    else:
        print "Received an invalid project_run_pk %s" % project_run_pk
