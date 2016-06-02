import csv

from django.shortcuts import render
from django.http import HttpResponse

from . import services

def index(request):
    data = services.overview()
    return render(request, 'index.html', data)

def meter_runs(request):
    """Render the table of exported MeterRun results in html"""
    data = services.meterruns_export()
    return render(request, 'project_run_table.html', data)

def csv_export(request):
    """Return a dump of all the MeterRuns in CSV form"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="meter_runs.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar'])

    return response