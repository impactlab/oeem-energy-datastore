from datastore import models
import numpy as np
import pandas as pd
import pytz


def create_project(spec):
    project = models.Project.objects.create(
        project_owner=spec["project_owner"],
        project_id=spec["project_id"],
        baseline_period_end=spec["baseline_period_end"],
        reporting_period_start=spec["reporting_period_start"],
        zipcode=spec["zipcode"],
    )

    records = []
    for trace_spec in spec["traces"]:
        trace = models.ConsumptionMetadata.objects.create(
            project=project,
            interpretation=trace_spec["interpretation"],
            unit=trace_spec["unit"],
        )

        dates = pd.date_range(
            start=trace_spec["start"],
            end=trace_spec["end"],
            freq=trace_spec["freq"],
            tz=pytz.UTC)

        nans = trace_spec["nans"]
        trace_value = trace_spec["value"]
        estimated = trace_spec["estimated"]

        for i, date in enumerate(dates):
            records.append(models.ConsumptionRecord(
                metadata=trace,
                start=date,
                value=(np.nan if i in nans else trace_value),
                estimated=(i in estimated),
            ))

    models.ConsumptionRecord.objects.bulk_create(records)
    return project
