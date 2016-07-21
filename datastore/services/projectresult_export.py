from datastore import models


def serialize(project_result):

    modeling_period_groups = project_result.modeling_period_groups.all()

    rows = []
    for modeling_period_group in modeling_period_groups:

        project_result_attrs = [
            'id',
            'eemeter_version',
            'meter_class',
        ]

        project_attrs = [
            'id',
            'project_id',
            'zipcode',
            'baseline_period_end',
            'reporting_period_start'
        ]

        modeling_period_group_attrs = [
            'id',
        ]

        period_attrs = [
            'id',
            'start_date',
            'end_date',
        ]

        derivative_aggregation_identifiers = [
            'trace_interpretation',
            'interpretation',
        ]

        derivative_aggregation_attrs = [
            'id',
            'baseline_value',
            'baseline_upper',
            'baseline_lower',
            'baseline_n',
            'reporting_value',
            'reporting_upper',
            'reporting_lower',
            'reporting_n',
        ]

        resp = {}

        project = project_result.project
        for attr in project_attrs:
            resp['project__' + attr] = getattr(project, attr)

        for attr in project_result_attrs:
            resp['project_result__' + attr] = getattr(project_result, attr)

        for attr in modeling_period_group_attrs:
            resp['modeling_period_group__' + attr] = \
                getattr(modeling_period_group, attr)

        modeling_period_baseline = modeling_period_group.baseline_period
        for attr in period_attrs:
            resp['baseline_period__' + attr] = \
                getattr(modeling_period_baseline, attr)

        modeling_period_reporting = modeling_period_group.reporting_period
        for attr in period_attrs:
            resp['reporting_period__' + attr] = \
                getattr(modeling_period_reporting, attr)

        derivative_aggregations = project_result.derivative_aggregations \
            .filter(modeling_period_group=modeling_period_group)\
            .order_by('-trace_interpretation')\
            .order_by('-interpretation')
        for derivative_aggregation in derivative_aggregations:
            prefix = 'derivative_aggregation__'
            for attr in derivative_aggregation_identifiers:
                prefix += getattr(derivative_aggregation, attr).lower() + '__'
            for attr in derivative_aggregation_attrs:
                resp[prefix + attr] = getattr(derivative_aggregation, attr)

        rows.append(resp)

    return rows


def projectresult_export():
    project_results = models.ProjectResult.objects.all()\
        .prefetch_related(
            "project",
            "derivative_aggregations",
            "modeling_period_groups",
            "modeling_period_groups__baseline_period",
            "modeling_period_groups__reporting_period")

    projectresults_serialized = []
    for pr in project_results:
        projectresults_serialized.extend(serialize(pr))

    headers = []
    if len(projectresults_serialized) > 0:
        headers = sorted(list(projectresults_serialized[0].keys()))

    return {'project_results': projectresults_serialized, 'headers': headers}
