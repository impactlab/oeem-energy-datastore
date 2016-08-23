from datastore import models
from django.db import connection


def _estimate_count(model):
    cursor = connection.cursor()
    cursor.execute("SELECT reltuples FROM pg_class "
                   "WHERE relname = '%s';" % model._meta.db_table)
    return int(cursor.fetchone()[0])


def overview():
    return {
        'project_count':
            models.Project.objects.count(),
        'consumptionmetadata_count':
            models.ConsumptionMetadata.objects.count(),
        'consumptionrecord_count':
            _estimate_count(models.ConsumptionRecord),
        'projectresult_count':
            models.ProjectResult.objects.count()
    }
