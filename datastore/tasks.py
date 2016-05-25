from __future__ import absolute_import
import traceback

from celery import shared_task
from celery.utils.log import get_task_logger

from datastore.models import Project, ProjectRun


logger = get_task_logger(__name__)


@shared_task
def execute_project_run(project_run_pk):

    try:
        project_run = ProjectRun.objects.get(pk=project_run_pk)
    except ProjectRun.DoesNotExist:
        logger.info("Received an invalid project_run_pk %s" % project_run_pk)
        return

    project_run.status = 'RUNNING'
    project_run.save()

    project = project_run.project

    logger.info(
        "Running {} meter for project {}"
        .format(project_run.meter_type, project.pk)
    )

    try:
        project.run_meter(meter_type=project_run.meter_type,
                          start_date=project_run.start_date,
                          end_date=project_run.end_date,
                          n_days=project_run.n_days)
        project_run.status = 'SUCCESS'

        logger.info(
            "Successfully ran {} meter for project {}"
            .format(project_run.meter_type, project.pk)
        )
    except:
        tb = traceback.format_exc()
        project_run.status = 'FAILED'
        project_run.traceback = tb

        logger.info(
            "Failed running {} meter for project {}:\n{}"
            .format(project_run.meter_type, project.pk, tb)
        )

    project_run.save()
