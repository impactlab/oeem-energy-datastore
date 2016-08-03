from datastore import models


def project_diagnostic_row(project):
    project_runs = project.projectrun_set.all()
    row = {
        'project_pk': project.id,
        'project_id': project.project_id,
        'project_result_count': project.project_results.count(),
        'project_run_count': len(project_runs),
        'project_run_count-PENDING': sum([
            1 for pr in project_runs if pr.status == 'PENDING'
        ]),
        'project_run_count-RUNNING': sum([
            1 for pr in project_runs if pr.status == 'RUNNING'
        ]),
        'project_run_count-SUCCESS': sum([
            1 for pr in project_runs if pr.status == 'SUCCESS'
        ]),
        'project_run_count-FAILED': sum([
            1 for pr in project_runs if pr.status == 'FAILED'
        ]),
        'consumption_metadata_count': project.consumptionmetadata_set.count(),
        'consumption_metadata_count-ELECTRICITY_CONSUMPTION_SUPPLIED': (
            project.consumptionmetadata_set
            .filter(interpretation='E_C_S').count()
        ),
        'consumption_metadata_count-ELECTRICITY_CONSUMPTION_NET': (
            project.consumptionmetadata_set
            .filter(interpretation='E_C_N').count()
        ),
        'consumption_metadata_count-ELECTRICITY_CONSUMPTION_TOTAL': (
            project.consumptionmetadata_set
            .filter(interpretation='E_C_T').count()
        ),
        'consumption_metadata_count-ELECTRICITY_ON_SITE_GENERATION_TOTAL': (
            project.consumptionmetadata_set
            .filter(interpretation='E_OSG_T').count()
        ),
        'consumption_metadata_count-ELECTRICITY_ON_SITE_GENERATION_CONSUMED': (
            project.consumptionmetadata_set
            .filter(interpretation='E_OSG_C').count()
        ),
        'consumption_metadata_count-ELECTRICITY_ON_SITE_GENERATION_UNCONSUMED':
        (
            project.consumptionmetadata_set
            .filter(interpretation='E_OSG_U').count()
        ),
        'consumption_metadata_count-NATURAL_GAS_CONSUMPTION_SUPPLIED': (
            project.consumptionmetadata_set
            .filter(interpretation='NG_C_S').count()
        ),
    }
    return row


def diagnostic_export():
    projects = models.Project.objects.all().prefetch_related(
        'project_results',
        'projectrun_set',
        'consumptionmetadata_set',
    ).order_by('project_id')

    return {
        'headers': [
            'project_pk',
            'project_id',
            'project_result_count',
            'project_run_count',
            'project_run_count-PENDING',
            'project_run_count-RUNNING',
            'project_run_count-SUCCESS',
            'project_run_count-FAILED',
            'consumption_metadata_count',
            'consumption_metadata_count-ELECTRICITY_CONSUMPTION_SUPPLIED',
            'consumption_metadata_count-ELECTRICITY_CONSUMPTION_NET',
            'consumption_metadata_count-ELECTRICITY_CONSUMPTION_TOTAL',
            'consumption_metadata_count-ELECTRICITY_ON_SITE_GENERATION_TOTAL',
            'consumption_metadata_count-'
                'ELECTRICITY_ON_SITE_GENERATION_CONSUMED',
            'consumption_metadata_count-'
                'ELECTRICITY_ON_SITE_GENERATION_UNCONSUMED',
            'consumption_metadata_count-NATURAL_GAS_CONSUMPTION_SUPPLIED',
        ],
        'rows': [
            project_diagnostic_row(project) for project in projects
        ],
    }
