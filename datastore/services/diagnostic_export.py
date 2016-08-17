from datastore import models


def project_diagnostic_row(project):
    project_runs = project.projectrun_set.all()

    trace_set = project.consumptionmetadata_set
    trace_count = trace_set.count()

    def status_count(status):
        return sum([1 for pr in project_runs if pr.status == status])

    row = {
        'project_pk': project.id,
        'project_id': project.project_id,
        'project_result_count': project.project_results.count(),
        'project_run_count': len(project_runs),
        'project_run_count-PENDING': status_count('PENDING'),
        'project_run_count-RUNNING': status_count('RUNNING'),
        'project_run_count-SUCCESS': status_count('SUCCESS'),
        'project_run_count-FAILED': status_count('FAILED'),
        'trace_count': trace_count,
        'trace_count-ELECTRICITY_CONSUMPTION_SUPPLIED':
            trace_set.filter(interpretation='E_C_S').count(),
        'trace_count-ELECTRICITY_CONSUMPTION_NET':
            trace_set.filter(interpretation='E_C_N').count(),
        'trace_count-ELECTRICITY_CONSUMPTION_TOTAL':
            trace_set.filter(interpretation='E_C_T').count(),
        'trace_count-ELECTRICITY_ON_SITE_GENERATION_TOTAL':
            trace_set.filter(interpretation='E_OSG_T').count(),
        'trace_count-ELECTRICITY_ON_SITE_GENERATION_CONSUMED':
            trace_set.filter(interpretation='E_OSG_C').count(),
        'trace_count-ELECTRICITY_ON_SITE_GENERATION_UNCONSUMED':
            trace_set.filter(interpretation='E_OSG_U').count(),
        'trace_count-NATURAL_GAS_CONSUMPTION_SUPPLIED':
            trace_set.filter(interpretation='NG_C_S').count(),
    }

    try:
        project_result = project.project_results.latest('pk')
    except models.ProjectResult.DoesNotExist:
        # maybe there was a failed (or incomplete) project run;
        # if latest can be found, show status and traceback
        try:
            project_run = project.projectrun_set.latest('pk')
        except models.ProjectRun.DoesNotExist:
            pass
        else:
            row.update({
                'project_run_id': project_run.id,
                'project_run_status': project_run.status,
                'project_run_traceback': project_run.traceback,
            })
    else:
        # project run details
        project_run = project_result.project_run
        if project_run is not None:
            row.update({
                'project_run_id': project_run.id,
                'project_run_status': project_run.status,
                'project_run_traceback': project_run.traceback,
            })

        # project result details
        energy_trace_model_results = \
            project_result.energy_trace_model_results \
                .order_by('energy_trace_id').order_by('modeling_period_id')
        derivative_aggregation_count = \
            project_result.derivative_aggregations.count()
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
            'derivative_aggregation_count': derivative_aggregation_count,
        })

        # modeling period group details
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

        # energy trace model result details
        for i, energy_trace_model_result in \
                enumerate(project_result.energy_trace_model_results.all()):
            start_date = energy_trace_model_result.input_start_date
            end_date = energy_trace_model_result.input_end_date
            records = energy_trace_model_result.energy_trace.records.all()
            record_count = records.count()
            row.update({
                'energy_trace_model_result_id|{}'.format(i):
                    energy_trace_model_result.pk,
                'energy_trace_model_result_status|{}'.format(i):
                    energy_trace_model_result.status,
                'energy_trace_model_result_traceback|{}'.format(i):
                    energy_trace_model_result.traceback,
                'energy_trace_model_result_trace_id|{}'.format(i):
                    energy_trace_model_result.energy_trace.pk,
                'energy_trace_model_result_trace_interpretation|{}'.format(i):
                    energy_trace_model_result.energy_trace.interpretation,
                'energy_trace_model_result_modeling_period_id|{}'.format(i):
                    energy_trace_model_result.modeling_period.pk,
                'energy_trace_model_result_modeling_period_interpretation|{}'
                    .format(i):
                    energy_trace_model_result.modeling_period.interpretation,
                'energy_trace_model_result_input_start_date|{}'.format(i):
                    start_date.isoformat() if start_date is not None else None,
                'energy_trace_model_result_input_end_date|{}'.format(i):
                    end_date.isoformat() if end_date is not None else None,
                'energy_trace_model_result_input_n_rows|{}'.format(i):
                    energy_trace_model_result.n,
                'energy_trace_model_result_records_start_date|{}'.format(i):
                    energy_trace_model_result.records_start_date,
                'energy_trace_model_result_records_end_date|{}'.format(i):
                    energy_trace_model_result.records_end_date,
                'energy_trace_model_result_records_count|{}'.format(i):
                    energy_trace_model_result.records_count,
            })

    # explanation
    has_derivative_aggregation = derivative_aggregation_count > 0
    has_no_energy_traces = trace_count == 0
    has_no_successful_meter_runs = status_count('SUCCESS') == 0
    has_explanation = (
        has_derivative_aggregation or
        has_no_energy_traces or
        has_no_successful_meter_runs
    )

    row.update({
        'EXPLANATION-has_no_energy_traces': has_no_energy_traces,
        'EXPLANATION-has_no_successful_meter_runs': has_no_successful_meter_runs,
        'EXPLANATION-has_derivative_aggregation': has_derivative_aggregation,
        'EXPLANATION-has_explanation': has_explanation,
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
        'project_results__energy_trace_model_results__energy_trace',
        'project_results__energy_trace_model_results__modeling_period',
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
        'trace_count',
        'trace_count-ELECTRICITY_CONSUMPTION_SUPPLIED',
        'trace_count-ELECTRICITY_CONSUMPTION_NET',
        'trace_count-ELECTRICITY_CONSUMPTION_TOTAL',
        'trace_count-ELECTRICITY_ON_SITE_GENERATION_TOTAL',
        'trace_count-ELECTRICITY_ON_SITE_GENERATION_CONSUMED',
        'trace_count-ELECTRICITY_ON_SITE_GENERATION_UNCONSUMED',
        'trace_count-NATURAL_GAS_CONSUMPTION_SUPPLIED',
        'project_run_id',
        'project_run_status',
        'project_run_traceback',
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
            'energy_trace_model_result_id|{}'.format(i),
            'energy_trace_model_result_status|{}'.format(i),
            'energy_trace_model_result_traceback|{}'.format(i),
            'energy_trace_model_result_trace_id|{}'.format(i),
            'energy_trace_model_result_trace_interpretation|{}'.format(i),
            'energy_trace_model_result_records_start_date|{}'.format(i),
            'energy_trace_model_result_records_end_date|{}'.format(i),
            'energy_trace_model_result_records_count|{}'.format(i),
            'energy_trace_model_result_modeling_period_id|{}'.format(i),
            'energy_trace_model_result_modeling_period_interpretation|{}'
                .format(i),
            'energy_trace_model_result_input_start_date|{}'.format(i),
            'energy_trace_model_result_input_end_date|{}'.format(i),
            'energy_trace_model_result_input_n_rows|{}'.format(i),
        ])

    headers.extend([
        'EXPLANATION-has_no_energy_traces',
        'EXPLANATION-has_no_successful_meter_runs',
        'EXPLANATION-has_derivative_aggregation',
        'EXPLANATION-has_explanation',
    ])

    return {
        'headers': headers,
        'rows': rows,
    }
