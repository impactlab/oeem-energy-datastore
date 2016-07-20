from datastore import models


def serialize(meter_run):

    attrs = [
        'id',
        'annual_savings',
        'annual_usage_baseline',
        'annual_usage_reporting',
        'cvrmse_baseline',
        'cvrmse_reporting',
        'gross_savings'
    ]
    project_attrs = [
        'baseline_period_end',
        'baseline_period_start',
        'latitude',
        'longitude',
        'project_id',
        'id',
        'reporting_period_end',
        'reporting_period_start',
        'weather_station'
    ]
    consumption_metadata_attrs = [
        'id',
        'interpretation',
        'unit'
    ]

    resp = {}
    for attr in attrs:
        resp[attr] = getattr(meter_run, attr)
    for attr in project_attrs:
        resp['project_' + attr] = getattr(meter_run.project, attr)
    for attr in consumption_metadata_attrs:
        resp['consumption_metadata_' + attr] = \
            getattr(meter_run.consumption_metadata, attr)

    return resp


def meterruns_export():
    meter_runs = models.MeterRun.objects.all()\
        .prefetch_related("project", "consumption_metadata")

    meter_runs_serialized = list(map(serialize, meter_runs))

    headers = []
    if len(meter_runs_serialized) > 0:
        headers = meter_runs_serialized[0].keys()

    return {'meter_runs': meter_runs_serialized, 'headers': headers}
