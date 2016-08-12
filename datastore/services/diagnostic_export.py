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

    try:
        project_result = project.project_results.latest('pk')
    except models.ProjectResult.DoesNotExist:
        project_result = None
    else:
        row.update({
            'project_result_id': project_result.id,
            'project_result_added': project_result.added.isoformat(),
            'modeling_period_count':
                project_result.modeling_periods.count(),
            'modeling_period_group_count':
                project_result.modeling_period_groups.count(),
            'energy_trace_model_result_count':
                project_result.energy_trace_model_results.count(),
            'derivative_count':
                sum([
                    etmr.derivatives.count()
                    for etmr in project_result.energy_trace_model_results.all()
                ]),
            'derivative_aggregation_count':
                project_result.derivative_aggregations.count(),
        })

    return row


def diagnostic_export():

    import pdb;pdb.set_trace()

    projects = models.Project.objects.all().prefetch_related(
        'project_results',
        'project_results__modeling_periods',
        'project_results__modeling_period_groups',
        'project_results__energy_trace_model_results',
        'project_results__energy_trace_model_results__derivatives',
        'project_results__derivative_aggregations',
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
            (
                'consumption_metadata_count-'
                'ELECTRICITY_ON_SITE_GENERATION_CONSUMED'
            ),
            (
                'consumption_metadata_count-'
                'ELECTRICITY_ON_SITE_GENERATION_UNCONSUMED'
            ),
            'consumption_metadata_count-NATURAL_GAS_CONSUMPTION_SUPPLIED',
            'project_result_id',
            'project_result_added',
            'modeling_period_count',
            'modeling_period_group_count',
            'energy_trace_model_result_count',
            'derivative_count',
            'derivative_aggregation_count',
        ],
        'rows': [
            project_diagnostic_row(project) for project in projects
        ],
    }
