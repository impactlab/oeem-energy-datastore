import pandas as pd

from django.shortcuts import render
from django.http import HttpResponse

from datastore import services


def index(request):
    data = services.overview()
    return render(request, 'index.html', data)


def meter_runs(request):
    """Render the table of exported MeterRun results in html"""
    data = services.projectresult_export()
    return render(request, 'project_result_table.html', data)


def projectresult_export_csv(request):
    """Return a dump of all the MeterRuns in CSV form"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = \
        'attachment; filename="project_results.csv"'

    data = services.projectresult_export()

    df = pd.DataFrame(data['project_results'])
    df.to_csv(response, columns=data['headers'], index=False)

    return response


def diagnostic_export_csv(request):
    """Return a dump of all the MeterRuns in CSV form"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = \
        'attachment; filename="diagnostics.csv"'

    data = services.diagnostic_export()

    df = pd.DataFrame(data['rows'])
    df.to_csv(response, columns=data['headers'], index=False)

    return response
