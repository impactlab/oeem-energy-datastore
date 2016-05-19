from __future__ import absolute_import
import logging

from celery import shared_task

from datastore.models import Project, ProjectRun

@shared_task
def execute_project_run(project_run_pk):
    project_run = ProjectRun.objects.get(pk=project_run_pk)
    if not project_run:
        logging.info("Received an invalid project_run_pk %s" % project_run_pk)
        return

    project = project_run.project
    if not project:
        logging.info("Asked to run a ProjectRun with no Project %s" % project_run_pk)
        return

    try:
        project.run_meter(meter_type=project_run.meter_type,
                          start_date=project_run.start_date,
                          end_date=project_run.end_date,
                          n_days=project_run.n_days)
        project_run.status = 'SUCCESS'
    except:
        project_run.status = 'FAILED'

    project_run.save()
