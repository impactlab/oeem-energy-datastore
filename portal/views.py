from django.shortcuts import render, render_to_response
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect
)
from django.core.urlresolvers import reverse

import logging

import pandas as pd

from portal.tasks import (
    generate_projectresult_export_csv,
    generate_diagnostic_export_csv,
)
from portal.models import CSVDownload
from datastore import services
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@login_required
def index(request):
    data = services.overview()
    return render(request, 'index.html', data)


@login_required
def projectresult_export_csv(request):
    """Return a dump of all the MeterRuns in CSV form"""
    csv_download = CSVDownload.objects.create(
        completed=False, filename="project_results"
    )
    generate_projectresult_export_csv.delay(csv_download.pk)
    url = reverse("download_csv") + "?csv_id={}".format(csv_download.pk)
    return HttpResponseRedirect(url)


@login_required
def diagnostic_export_csv(request):
    """Return a dump of all the MeterRuns in CSV form"""
    csv_download = CSVDownload.objects.create(
        completed=False, filename="diagnostics"
    )
    generate_diagnostic_export_csv.delay(csv_download.pk)
    url = reverse("download_csv") + "?csv_id={}".format(csv_download.pk)
    return HttpResponseRedirect(url)


@login_required
def download_csv(request):
    csv_id = request.GET.get("csv_id")
    try:
        csv_download = CSVDownload.objects.get(pk=csv_id)
    except CSVDownload.objects.DoesNotExist:
        return HttpResponseForbidden()

    if csv_download.completed:
        logger.info("CSV creation finished; sending download.")
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="{}.csv"'
            .format(csv_download.filename)
        )
        response.write(csv_download.content)
        return response
    else:
        logger.info("CSV not completed, re-rendering download waiting page.")
        return render_to_response("download_csv.html",
                                  {"csv_id": csv_download.pk})
