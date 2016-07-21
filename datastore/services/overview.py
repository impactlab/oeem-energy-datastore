from datastore import models


def overview():
    return {
        'project_count': models.Project.objects.count(),
        'consumptionmetadata_count':
            models.ConsumptionMetadata.objects.count(),
        'consumptionrecord_count': models.ConsumptionRecord.objects.count(),
        'projectresult_count': models.ProjectResult.objects.count()
    }
