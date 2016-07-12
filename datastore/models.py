from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import now
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver

from eemeter.structures import (
    EnergyTrace,
    EnergyTraceSet,
    Intervention,
    ZIPCodeSite,
    ModelingPeriod,
    Project as EEMeterProject,
)
from eemeter.io.serializers import ArbitraryStartSerializer
from eemeter.ee.meter import EnergyEfficiencyMeter

from warnings import warn
from datetime import timedelta, datetime
import numpy as np
import json
from collections import defaultdict, OrderedDict
import itertools

METER_CLASS_CHOICES = {
    'EnergyEfficiencyMeter': EnergyEfficiencyMeter,
}

FUEL_TYPE_CHOICES = [
    ('E', 'electricity'),
    ('NG', 'natural_gas'),
]

UNIT_CHOICES = [
    ('KWH', 'kWh'),
    ('THM', 'therm'),
]

PROJECT_ATTRIBUTE_DATA_TYPE_CHOICES = [
    ('BOOLEAN', 'boolean_value'),
    ('CHAR', 'char_value'),
    ('DATE', 'date_value'),
    ('DATETIME', 'datetime_value'),
    ('FLOAT', 'float_value'),
    ('INTEGER', 'integer_value'),
]

def _json_clean(value):
    if value is None or np.isnan(value) or np.isinf(value):
        return None
    else:
        return value


@python_2_unicode_compatible
class ProjectOwner(models.Model):
    user = models.OneToOneField(User)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'ProjectOwner {}'.format(self.user.username)

@python_2_unicode_compatible
class Project(models.Model):
    project_owner = models.ForeignKey(ProjectOwner)
    project_id = models.CharField(max_length=255, null=False, unique=True)
    baseline_period_start = models.DateTimeField(blank=True, null=True)
    baseline_period_end = models.DateTimeField(blank=True, null=True)
    reporting_period_start = models.DateTimeField(blank=True, null=True)
    reporting_period_end = models.DateTimeField(blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    weather_station = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'Project {}'.format(self.project_id)

    @property
    def lat_lng(self):
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        else:
            return None

    def eemeter_project(self):
        cm_set = self.consumptionmetadata_set.all()
        consumption = [cm.eemeter_consumption_data() for cm in cm_set]
        consumption_metadata_ids = [cm.id for cm in cm_set]
        energy_trace_set = EnergyTraceSet(consumption,
                                          consumption_metadata_ids)
        interventions = [self._eemeter_intervention()]
        site = self._eemeter_location()

        return EEMeterProject(energy_trace_set, interventions, site)

    def _eemeter_intervention(self):
        return Intervention(self.baseline_period_end, self.reporting_period_start)

    def _eemeter_location(self):
        return ZIPCodeSite(zipcode=self.zipcode)

    def run_meter(self, meter_class='EnergyEfficiencyMeter', start_date=None,
                  end_date=None, n_days=None, meter_settings=None):
        """
        If possible, run the meter specified by meter_class.

        Parameters
        ----------
        meter_class: string
            One of the keys in METER_CLASS_CHOICES

        start_date: datetime

        end_data: datetime

        n_days: int

        meter_settings: dict
            Dictionary of extra settings to send to the meter.

        """
        try:
            project = self.eemeter_project()
        except ValueError:
            message = (
                "Cannot create eemeter project; skipping project id={}."
                .format(self.project_id)
            )
            warn(message)
            return None

        meter = self._get_meter(meter_class, settings=meter_settings)
        results = meter.evaluate(project)
        meter_runs = []
        for energy_trace_label in results['energy_trace_labels']:
            meter_run = self._energy_trace_results_as_meter_run(
                energy_trace_label, results, meter_class, meter_settings)
            meter_run.save()
            meter_runs.append(meter_run)

            # self._save_daily_and_monthly_timeseries(project, meter, meter_run, model, model_parameters_baseline, model_parameters_reporting, timeseries_period)

        return meter_runs

    def _get_meter(self, meter_class, settings=None):
        MeterClass = METER_CLASS_CHOICES.get(meter_class, None)
        if MeterClass is None:
            raise ValueError("Received an invald meter_class %s" % meter_class)
        if settings is None:
            settings = {}
        meter = MeterClass(settings=settings)
        return meter

    def _energy_trace_results_as_meter_run(
            self, energy_trace_label, results, meter_class, meter_settings):

        interpretations = sorted(results['modeling_period_interpretations']
                               .values())
        if ['BASELINE', 'REPORTING'] != interpretations:
            warn("Unsupported modeling period interpretation configuration")

        interpretation_mapping = {
            interpretation: label
            for label, interpretation in
                results['modeling_period_interpretations'].items()
        }

        baseline_label = interpretation_mapping['BASELINE']
        baseline_results = results['modeled_energy_traces'] \
                [(baseline_label, energy_trace_label)]

        reporting_label = interpretation_mapping['REPORTING']
        reporting_results = results['modeled_energy_traces']\
                [(reporting_label, energy_trace_label)]

        kwargs = {
            "project": self,
            "consumption_metadata": ConsumptionMetadata.objects.get(
                pk=energy_trace_label),
            "serialization": "",
            "meter_class": meter_class,
            "meter_settings": meter_settings,
            "gross_savings": None,
            "annual_savings": None,
        }

        if baseline_results['status'] == 'SUCCESS':
            kwargs.update({
                "annual_usage_baseline":
                    baseline_results['annualized_weather_normal'][0],
                "cvrmse_baseline":
                    baseline_results['cvrmse'],
                "model_parameter_json_baseline": None,
            })

        if reporting_results['status'] == 'SUCCESS':
            kwargs.update({
                "annual_usage_reporting":
                    reporting_results['annualized_weather_normal'][0],
                "cvrmse_reporting":
                    reporting_results['cvrmse'],
                "model_parameter_json_reporting": None,
            })

        meter_run = MeterRun(**kwargs)
        return meter_run

    # def _save_daily_and_monthly_timeseries(self, project, meter, meter_run, model, model_parameters_baseline, model_parameters_reporting, period):
    #
    #     # record time series of usage for baseline and reporting
    #     avg_temps = project.weather_source.daily_temperatures(
    #             period, meter.temperature_unit_str)
    #
    #     values_baseline = model.transform(avg_temps, model_parameters_baseline)
    #     values_reporting = model.transform(avg_temps, model_parameters_reporting)
    #
    #     month_names = [period.start.strftime("%Y-%m")]
    #
    #     month_groups_baseline = defaultdict(list)
    #     month_groups_reporting = defaultdict(list)
    #
    #     for value_baseline, value_reporting, days in zip(values_baseline, values_reporting, range(period.timedelta.days)):
    #         date = period.start + timedelta(days=days)
    #
    #         daily_usage_baseline = DailyUsageBaseline(meter_run=meter_run, value=value_baseline, date=date)
    #         daily_usage_baseline.save()
    #
    #         daily_usage_reporting = DailyUsageReporting(meter_run=meter_run, value=value_reporting, date=date)
    #         daily_usage_reporting.save()
    #
    #         # track monthly usage as well
    #         current_month = date.strftime("%Y-%m")
    #         if not current_month == month_names[-1]:
    #             month_names.append(current_month)
    #
    #         month_groups_baseline[current_month].append(value_baseline)
    #         month_groups_reporting[current_month].append(value_reporting)
    #
    #     for month_name in month_names:
    #         baseline_values = month_groups_baseline[month_name]
    #         reporting_values = month_groups_reporting[month_name]
    #
    #         monthly_average_baseline = 0 if baseline_values == [] else np.nanmean(baseline_values)
    #         monthly_average_reporting = 0 if reporting_values == [] else np.nanmean(reporting_values)
    #
    #         dt = datetime.strptime(month_name, "%Y-%m")
    #         monthly_average_usage_baseline = MonthlyAverageUsageBaseline(meter_run=meter_run, value=monthly_average_baseline, date=dt)
    #         monthly_average_usage_baseline.save()
    #
    #         monthly_average_usage_reporting = MonthlyAverageUsageReporting(meter_run=meter_run, value=monthly_average_reporting, date=dt)
    #         monthly_average_usage_reporting.save()

    @staticmethod
    def recent_meter_runs(project_pks=[]):
        """
        Returns most recently create MeterRun objects for each
        ConsumptionMetadata object associated with the set of projects.
        NOTE: not an instance method!!

        Parameters
        ----------
        project_pks : list of int, default []
            Primary keys of projects for which to get recent meter runs. If
            an empty list, will get recent meter runs for every project in
            the database.

        Returns
        -------
        out : dict of dict
            Dictionary in which project primary keys are keys and associated
            meter runs are values. E.g.::

            { # keys are primary keys of Project objects
                1: { # keys are primary keys of ConsumptionMetadata objects
                    1: {
                        "meter_run": <MeterRun object>,
                        "fuel_type": "E"
                    },
                    2: {
                        "meter_run": <MeterRun object>,
                        "fuel_type": "NG"
                    }
                },
                2: {
                    3: {
                        "meter_run": <MeterRun object>,
                        "fuel_type": "E"
                    },
                    4: {
                        "meter_run": <MeterRun object>,
                        "fuel_type": "NG"
                    }
                }
            }

        """

        meter_run_query = '''
          SELECT DISTINCT ON (consumption.id)
            meter.*,
            consumption.fuel_type AS fuel_type_
          FROM datastore_meterrun AS meter
          JOIN datastore_consumptionmetadata AS consumption
            ON meter.consumption_metadata_id = consumption.id
          JOIN datastore_project AS project
            ON meter.project_id = project.id
        '''

        qargs = []

        if project_pks:
            meter_run_query += '''
              WHERE project.id IN %s
            '''
            qargs.append(tuple(project_pks))

        meter_run_query += '''
          ORDER BY consumption.id,
            meter.added DESC
        '''

        meter_runs = MeterRun.objects.raw(meter_run_query, qargs)

        # initialize with ordereddict for each project.
        results = defaultdict(OrderedDict)

        for meter_run in meter_runs:

            results[meter_run.project_id][meter_run.consumption_metadata_id] = {
                'meter_run': meter_run,
                'fuel_type': meter_run.fuel_type_,
            }

        return results

    def attributes(self):
        return self.projectattribute_set.all()


@python_2_unicode_compatible
class ProjectRun(models.Model):
    """Encapsulates the request to run a Project's meters, pointing to Celery objects and Meter results."""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('FAILED', 'Failed'),
        ('SUCCESS', 'Success')
    )
    METER_TYPE_CHOICES = (
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    )
    project = models.ForeignKey(Project)
    status = models.CharField(max_length=250, choices=STATUS_CHOICES, default="PENDING")
    meter_class = models.CharField(max_length=250, null=True, default="EnergyEfficiencyMeter")
    meter_settings = JSONField(null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    n_days = models.IntegerField(null=True)
    traceback = models.CharField(max_length=10000, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'ProjectRun(project_id={}, status={})'.format(self.project.project_id, self.status)


@python_2_unicode_compatible
class ProjectAttributeKey(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=25, choices=PROJECT_ATTRIBUTE_DATA_TYPE_CHOICES)

    def __str__(self):
        return u'"{}" ({}, {})'.format(self.display_name, self.name, self.data_type)


@python_2_unicode_compatible
class ProjectAttribute(models.Model):
    project = models.ForeignKey(Project)
    key = models.ForeignKey(ProjectAttributeKey)
    boolean_value = models.NullBooleanField(blank=True, null=True)
    char_value = models.CharField(max_length=100, blank=True, null=True)
    date_value = models.DateField(blank=True, null=True)
    datetime_value = models.DateTimeField(blank=True, null=True)
    float_value = models.FloatField(blank=True, null=True)
    integer_value = models.IntegerField(blank=True, null=True)

    def value(self):
        if self.key.data_type == "BOOLEAN":
            return self.boolean_value
        elif self.key.data_type == "CHAR":
            return self.char_value
        elif self.key.data_type == "DATE":
            return self.date_value
        elif self.key.data_type == "DATETIME":
            return self.datetime_value
        elif self.key.data_type == "FLOAT":
            return self.float_value
        elif self.key.data_type == "INTEGER":
            return self.integer_value
        else:
            return None

    def __str__(self):
        return u'({}, {}, project:{})'.format(self.key.name, self.value(), self.project)


@python_2_unicode_compatible
class ProjectBlock(models.Model):
    name = models.CharField(max_length=255)
    projects = models.ManyToManyField(Project)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'(name={}, n_projects={})'.format(self.name, self.projects.count())

    def run_meters(self, meter_class='DefaultResidentialMeter', start_date=None, end_date=None, n_days=None):
        """ Run meter for each project in the project block.
        """
        for project in self.projects.all():
            project.run_meter(meter_class, start_date, end_date, n_days)

    def compute_summary_timeseries(self):
        """ Compute aggregate timeseries for all projects in project block.
        """
        data_by_fuel_type = defaultdict(lambda: {
            "baseline_by_month": defaultdict(list),
            "baseline_by_date": defaultdict(list),
            "actual_by_month": defaultdict(list),
            "actual_by_date": defaultdict(list),
            "reporting_by_month": defaultdict(list),
            "reporting_by_date": defaultdict(list),
            "n_completed_projects_by_date": defaultdict(lambda: 0),
        })

        for project in self.projects.all():
            for meter_run in project.recent_meter_runs():

                fuel_type = meter_run.consumption_metadata.fuel_type
                dailyusagebaseline_set = meter_run.dailyusagebaseline_set.all()
                dailyusagereporting_set = meter_run.dailyusagereporting_set.all()
                assert len(dailyusagebaseline_set) == len(dailyusagereporting_set)

                fuel_type_data = data_by_fuel_type[fuel_type]
                baseline_by_month = fuel_type_data["baseline_by_month"]
                baseline_by_date = fuel_type_data["baseline_by_date"]
                actual_by_month = fuel_type_data["actual_by_month"]
                actual_by_date = fuel_type_data["actual_by_date"]
                reporting_by_month = fuel_type_data["reporting_by_month"]
                reporting_by_date = fuel_type_data["reporting_by_date"]
                n_completed_projects_by_date = fuel_type_data["n_completed_projects_by_date"]

                for daily_usage_baseline, daily_usage_reporting in \
                        zip(dailyusagebaseline_set, dailyusagereporting_set):

                    # should be the same as the month for the reporting period
                    date = daily_usage_baseline.date
                    month = date.strftime("%Y-%m")

                    baseline_value = daily_usage_baseline.value
                    reporting_value = daily_usage_reporting.value

                    if date > project.reporting_period_start.date():
                        actual_value = reporting_value
                        n_completed_projects_by_date[date] += 1
                    else:
                        actual_value = baseline_value

                    baseline_by_month[month].append(baseline_value)
                    baseline_by_date[date].append(baseline_value)
                    actual_by_month[month].append(actual_value)
                    actual_by_date[date].append(actual_value)
                    reporting_by_month[month].append(reporting_value)
                    reporting_by_date[date].append(reporting_value)

        for fuel_type, fuel_type_data in data_by_fuel_type.items():

            baseline_by_month = fuel_type_data["baseline_by_month"]
            baseline_by_date = fuel_type_data["baseline_by_date"]
            actual_by_month = fuel_type_data["actual_by_month"]
            actual_by_date = fuel_type_data["actual_by_date"]
            reporting_by_month = fuel_type_data["reporting_by_month"]
            reporting_by_date = fuel_type_data["reporting_by_date"]
            n_completed_projects_by_date = fuel_type_data["n_completed_projects_by_date"]

            date_labels = sorted(baseline_by_date.keys())
            month_labels = sorted(baseline_by_month.keys())

            fuel_type_summary = FuelTypeSummary(project_block=self,
                    fuel_type=fuel_type)
            fuel_type_summary.save()

            for date in date_labels:
                DailyUsageSummaryBaseline(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(baseline_by_date[date]), date=date).save()
                DailyUsageSummaryActual(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(actual_by_date[date]), date=date,
                        n_projects=n_completed_projects_by_date[date]).save()
                DailyUsageSummaryReporting(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(reporting_by_date[date]), date=date).save()

            for month in month_labels:
                date = datetime.strptime(month, "%Y-%m").date()
                MonthlyUsageSummaryBaseline(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(baseline_by_month[month]), date=date).save()
                MonthlyUsageSummaryActual(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(actual_by_month[month]), date=date,
                        n_projects=n_completed_projects_by_date[date]).save()
                MonthlyUsageSummaryReporting(fuel_type_summary=fuel_type_summary,
                        value=np.nansum(reporting_by_month[month]), date=date).save()

    def recent_summaries(self):
        fuel_types = set([fts['fuel_type'] for fts in self.fueltypesummary_set.values('fuel_type')])
        return [self.fueltypesummary_set.filter(fuel_type=fuel_type).latest('added') for fuel_type in fuel_types]


@python_2_unicode_compatible
class ConsumptionMetadata(models.Model):
    fuel_type = models.CharField(max_length=3, choices=FUEL_TYPE_CHOICES)
    unit = models.CharField(max_length=3, choices=UNIT_CHOICES)
    project = models.ForeignKey(Project, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def eemeter_consumption_data(self):
        records = [r.eemeter_record() for r in self.records.all()]
        fuel_type = dict(FUEL_TYPE_CHOICES)[self.fuel_type]
        unit_name = dict(UNIT_CHOICES)[self.unit]
        interpretation = "{}_CONSUMPTION_SUPPLIED".format(fuel_type.upper())
        return EnergyTrace(interpretation, records=records, unit=unit_name,
                           serializer=ArbitraryStartSerializer())

    def __str__(self):
        n = len(self.records.all())
        return u'ConsumptionMetadata(fuel_type={}, unit={}, n={})'.format(self.fuel_type, self.unit, n)


@python_2_unicode_compatible
class ConsumptionRecord(models.Model):
    metadata = models.ForeignKey(ConsumptionMetadata, related_name="records")
    start = models.DateTimeField()
    value = models.FloatField(blank=True, null=True)
    estimated = models.BooleanField()

    def __str__(self):
        return u'Consumption(start={}, value={}, estimated={})'.format(self.start, self.value, self.estimated)

    class Meta:
        ordering = ['start']

    def eemeter_record(self):
        return {"start": self.start, "value": self.value, "estimated": self.estimated }

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class MeterRun(models.Model):
    project = models.ForeignKey(Project)
    consumption_metadata = models.ForeignKey(ConsumptionMetadata)
    serialization = models.CharField(max_length=100000, blank=True, null=True)
    annual_usage_baseline = models.FloatField(blank=True, null=True)
    annual_usage_reporting = models.FloatField(blank=True, null=True)
    gross_savings = models.FloatField(blank=True, null=True)
    annual_savings = models.FloatField(blank=True, null=True)
    meter_class = models.CharField(max_length=250, blank=True, null=True)
    meter_settings = JSONField(null=True)
    model_parameter_json_baseline = models.CharField(max_length=10000, blank=True, null=True)
    model_parameter_json_reporting = models.CharField(max_length=10000, blank=True, null=True)
    cvrmse_baseline = models.FloatField(blank=True, null=True)
    cvrmse_reporting = models.FloatField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'MeterRun(project_id={}, valid={})'.format(self.project.project_id, self.valid_meter_run())

    def annual_usage_baseline_clean(self):
        return _json_clean(self.annual_usage_baseline)

    def annual_usage_reporting_clean(self):
        return _json_clean(self.annual_usage_reporting)

    def gross_savings_clean(self):
        return _json_clean(self.gross_savings)

    def annual_savings_clean(self):
        return _json_clean(self.annual_savings)

    def cvrmse_baseline_clean(self):
        return _json_clean(self.cvrmse_baseline)

    def cvrmse_reporting_clean(self):
        return _json_clean(self.cvrmse_reporting)

    @property
    def fuel_type(self):
        return self.consumption_metadata.fuel_type

    def valid_meter_run(self, threshold=20):
        if self.cvrmse_baseline is None or self.cvrmse_reporting is None:
            return False
        return self.cvrmse_baseline < threshold and self.cvrmse_reporting < threshold


@python_2_unicode_compatible
class DailyUsageBaseline(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'DailyUsageBaseline(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class DailyUsageReporting(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'DailyUsageReporting(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class MonthlyAverageUsageBaseline(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'MonthlyAverageUsageBaseline(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class MonthlyAverageUsageReporting(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'MonthlyAverageUsageReporting(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class FuelTypeSummary(models.Model):
    project_block = models.ForeignKey(ProjectBlock)
    fuel_type = models.CharField(max_length=3, choices=FUEL_TYPE_CHOICES)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'FuelTypeSummary(project_block={}, fuel_type={})'.format(self.project_block, self.fuel_type)


@python_2_unicode_compatible
class DailyUsageSummaryBaseline(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'DailyUsageSummaryBaseline(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class DailyUsageSummaryActual(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()
    n_projects = models.IntegerField()

    def __str__(self):
        return u'DailyUsageSummaryActual(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

    def value_clean(self):
        return _json_clean(self.value)

@python_2_unicode_compatible
class DailyUsageSummaryReporting(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'DailyUsageSummaryReporting(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class MonthlyUsageSummaryBaseline(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'MonthlyUsageSummaryBaseline(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class MonthlyUsageSummaryActual(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()
    n_projects = models.IntegerField()

    def __str__(self):
        return u'MonthlyUsageSummaryActual(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class MonthlyUsageSummaryReporting(models.Model):
    fuel_type_summary = models.ForeignKey(FuelTypeSummary)
    value = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return u'MonthlyUsageSummaryReporting(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']


# # if project set changed, recompute the summary timeseries.
# TODO if needed, uncomment when this can be moved into the background, otherwise too slow.
# @receiver(post_init, sender=ProjectBlock)
# def project_block_compute_summary_timeseries(sender, instance, **kwargs):
#     instance.__projects = instance.projects
#
# @receiver(post_save, sender=ProjectBlock)
# def project_block_compute_summary_timeseries(sender, instance, **kwargs):
#     if instance.__projects != instance.projects:
#         instance.compute_summary_timeseries()
#         instance.__projects = instance.projects

@receiver(post_save, sender=User)
def create_project_owner(sender, instance, **kwargs):
    project_owner, created = ProjectOwner.objects.get_or_create(user=instance)
