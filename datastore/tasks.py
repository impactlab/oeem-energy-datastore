from __future__ import absolute_import
import logging
import traceback

from celery import shared_task
from celery.utils.log import get_task_logger

from datastore.models import ProjectRun


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
        .format(project_run.meter_class, project.pk)
    )

    try:
        project.run_meter(meter_class=project_run.meter_class,
                          meter_settings=project_run.meter_settings,
                          project_run=project_run)
        project_run.status = 'SUCCESS'
        logger.info(
            "Successfully ran {} meter for project {}"
            .format(project_run.meter_class, project.pk)
        )
    except:
        tb = traceback.format_exc()
        project_run.status = 'FAILED'
        project_run.traceback = tb
        logger.info(
            "Failed running {} meter for project {}:\n{}"
            .format(project_run.meter_class, project.pk, tb)
        )
        logging.error(traceback.print_exc())

    project_run.save()
