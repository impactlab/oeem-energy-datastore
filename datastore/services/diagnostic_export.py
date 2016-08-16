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
        energy_trace_model_results = project_result.energy_trace_model_results
        row.update({
            'project_result_id': project_result.id,
            'project_result_added': project_result.added.isoformat(),
            'modeling_period_count':
                project_result.modeling_periods.count(),
            'modeling_period_group_count':
                project_result.modeling_period_groups.count(),
            'energy_trace_model_result_count':
                energy_trace_model_results.count(),
            'energy_trace_model_result_count-FAILURE':
                energy_trace_model_results
                .filter(status='FAILURE').count(),
            'energy_trace_model_result_count-SUCCESS':
                energy_trace_model_results
                .filter(status='SUCCESS').count(),
            'derivative_count':
                sum([
                    etmr.derivatives.count()
                    for etmr in energy_trace_model_results.all()
                ]),
            'derivative_aggregation_count':
                project_result.derivative_aggregations.count(),
        })

        for i, modeling_period_group in \
                enumerate(project_result.modeling_period_groups.all()):
            baseline_period = modeling_period_group.baseline_period
            reporting_period = modeling_period_group.reporting_period
            row.update({
                'modeling_period_start_date-BASELINE|{}'.format(i):
                    baseline_period.start_date.isoformat()
                    if baseline_period.start_date is not None else None,
                'modeling_period_end_date-BASELINE|{}'.format(i):
                    baseline_period.end_date.isoformat()
                    if baseline_period.end_date is not None else None,
                'modeling_period_n_days-BASELINE|{}'.format(i):
                    baseline_period.n_days(),
                'modeling_period_start_date-REPORTING|{}'.format(i):
                    reporting_period.start_date.isoformat()
                    if reporting_period.start_date is not None else None,
                'modeling_period_end_date-REPORTING|{}'.format(i):
                    reporting_period.end_date.isoformat()
                    if reporting_period.end_date is not None else None,
                'modeling_period_n_days-REPORTING|{}'.format(i):
                    reporting_period.n_days(),
                'modeling_period_n_gap_days|{}'.format(i):
                    modeling_period_group.n_gap_days(),
            })

        for i, energy_trace_model_result in \
                enumerate(project_result.energy_trace_model_results.all()):
            start_date = energy_trace_model_result.input_start_date
            end_date = energy_trace_model_result.input_end_date
            row.update({
                'energy_trace_model_result_input_start_date|{}'.format(i):
                    start_date.isoformat() if start_date is not None else None,
                'energy_trace_model_result_input_end_date|{}'.format(i):
                    end_date.isoformat() if end_date is not None else None,
                'energy_trace_model_result_input_n_rows|{}'.format(i):
                    energy_trace_model_result.n,
            })

    return row


def get_max_n(rows, column_template):
    ns = [
        int(k.split('|')[-1])
        for row in rows
        for k in row.keys() if k.startswith(column_template)
    ]

    return max(ns) if ns != [] else 0


def diagnostic_export():

    projects = models.Project.objects.all().prefetch_related(
        'project_results',
        'project_results__modeling_period_groups',
        'project_results__modeling_period_groups__baseline_period',
        'project_results__modeling_period_groups__reporting_period',
        'project_results__energy_trace_model_results',
        'project_results__energy_trace_model_results__derivatives',
        'project_results__derivative_aggregations',
        'projectrun_set',
        'consumptionmetadata_set',
    ).order_by('project_id')

    headers = [
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
        'energy_trace_model_result_count-SUCCESS',
        'energy_trace_model_result_count-FAILURE',
        'derivative_count',
        'derivative_aggregation_count',
    ]

    rows = [project_diagnostic_row(project) for project in projects]

    # add extra rows for modeling periods
    n_mp_max = get_max_n(rows, 'modeling_period_start_date-BASELINE')
    for i in range(n_mp_max + 1):
        headers.extend([
            'modeling_period_start_date-BASELINE|{}'.format(i),
            'modeling_period_end_date-BASELINE|{}'.format(i),
            'modeling_period_n_days-BASELINE|{}'.format(i),
            'modeling_period_start_date-REPORTING|{}'.format(i),
            'modeling_period_end_date-REPORTING|{}'.format(i),
            'modeling_period_n_days-REPORTING|{}'.format(i),
            'modeling_period_n_gap_days|{}'.format(i),
        ])

    # add extra rows for energy energy_trace_model_results
    n_etmr_max = get_max_n(rows, 'energy_trace_model_result_input_start_date')
    for i in range(n_etmr_max):
        headers.extend([
            'energy_trace_model_result_input_start_date|{}'.format(i),
            'energy_trace_model_result_input_end_date|{}'.format(i),
            'energy_trace_model_result_input_n_rows|{}'.format(i),
        ])

    return {
        'headers': headers,
        'rows': rows,
    }
