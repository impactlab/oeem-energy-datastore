from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def project_runs(request, id=None):
    """Render the table of results for a ProjectRun in an html table"""
    data = {'rows': [
        {'id': 1},
        {'id': 2}
    ]}
    return render(request, 'project_run_table.html', data)