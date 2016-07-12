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

INTERPRETATION_CHOICES = [
    ('E_C_S', 'ELECTRICITY_CONSUMPTION_SUPPLIED'),
    ('E_C_T', 'ELECTRICITY_CONSUMPTION_TOTAL'),
    ('E_C_N', 'ELECTRICITY_CONSUMPTION_NET'),
    ('E_OSG_T', 'ELECTRICITY_ON_SITE_GENERATION_TOTAL'),
    ('E_OSG_C', 'ELECTRICITY_ON_SITE_GENERATION_CONSUMED'),
    ('E_OSG_U', 'ELECTRICITY_ON_SITE_GENERATION_UNCONSUMED'),
    ('NG_C_S', 'NATURAL_GAS_CONSUMPTION_SUPPLIED'),
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

    def run_meter(self, meter_class='EnergyEfficiencyMeter',
                  meter_settings=None):
        """
        If possible, run the meter specified by meter_class.

        Parameters
        ----------
        meter_class : str
            One of the keys in METER_CLASS_CHOICES
        meter_settings : dict
            Dictionary of extra settings to send to the meter.

        Returns
        -------
        meter_runs : list of MeterRun objects.
            Outputted meter runs
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
                        "interpretation": "E"
                    },
                    2: {
                        "meter_run": <MeterRun object>,
                        "interpretation": "NG"
                    }
                },
                2: {
                    3: {
                        "meter_run": <MeterRun object>,
                        "interpretation": "E"
                    },
                    4: {
                        "meter_run": <MeterRun object>,
                        "interpretation": "NG"
                    }
                }
            }

        """

        meter_run_query = '''
          SELECT DISTINCT ON (consumption.id)
            meter.*,
            consumption.interpretation AS interpretation_
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
                'interpretation': meter_run.interpretation_,
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

    def run_meters(self, meter_class='EnergyEfficiencyMeter', meter_settings=None):
        """ Run meter for each project in the project block.
        """
        for project in self.projects.all():
            project.run_meter(meter_class, meter_settings)


@python_2_unicode_compatible
class ConsumptionMetadata(models.Model):
    interpretation = models.CharField(max_length=16, choices=INTERPRETATION_CHOICES)
    unit = models.CharField(max_length=3, choices=UNIT_CHOICES)
    project = models.ForeignKey(Project, blank=True, null=True)
    label = models.CharField(max_length=140, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def eemeter_consumption_data(self):
        records = [r.eemeter_record() for r in self.records.all()]
        interpretation = dict(INTERPRETATION_CHOICES)[self.interpretation]
        unit_name = dict(UNIT_CHOICES)[self.unit]
        return EnergyTrace(interpretation, records=records, unit=unit_name,
                           serializer=ArbitraryStartSerializer())

    def __str__(self):
        n = len(self.records.all())
        return u'ConsumptionMetadata(interpretation={}, unit={}, n={})'.format(self.interpretation, self.unit, n)


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
    def interpretation(self):
        return self.consumption_metadata.interpretation

    def valid_meter_run(self, threshold=20):
        if self.cvrmse_baseline is None or self.cvrmse_reporting is None:
            return False
        return self.cvrmse_baseline < threshold and self.cvrmse_reporting < threshold


@receiver(post_save, sender=User)
def create_project_owner(sender, instance, **kwargs):
    project_owner, created = ProjectOwner.objects.get_or_create(user=instance)
