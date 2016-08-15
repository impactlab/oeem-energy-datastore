from celery import shared_task
from celery.utils.log import get_task_logger

import csv

from six import StringIO
import pandas as pd

from portal.models import CSVDownload
from datastore.services import (
    diagnostic_export,
    projectresult_export,
)

logger = get_task_logger(__name__)


def save_csv(csv_download_pk, data):
    csv_download = CSVDownload.objects.get(pk=csv_download_pk)
    string = StringIO()
    df = pd.DataFrame(data['rows'])
    df.to_csv(string, columns=data['headers'], index=False,
              quoting=csv.QUOTE_NONNUMERIC)
    csv_download.content = string.getvalue()
    csv_download.completed = True
    csv_download.save()
    logger.info("Saved CSVDownload(pk={})".format(csv_download.pk))


@shared_task
def generate_projectresult_export_csv(csv_download_pk):
    logger.info("Creating CSVDownload(pk={}) - project result export"
                .format(csv_download_pk))
    save_csv(csv_download_pk, projectresult_export())


@shared_task
def generate_diagnostic_export_csv(csv_download_pk):
    logger.info("Creating CSVDownload(pk={}) - diagnostic export"
                .format(csv_download_pk))
    save_csv(csv_download_pk, diagnostic_export())
