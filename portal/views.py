from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def project_runs(request, id=None):
    """Render the table of results for a ProjectRun in an html table"""

    # TODO: move into a model or service object or ...
    from datastore import models
    meter_runs = models.MeterRun.objects.all().prefetch_related("project", "consumption_metadata")

    data = {'meter_runs': meter_runs}

    return render(request, 'project_run_table.html', data)