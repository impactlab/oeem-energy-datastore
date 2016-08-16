from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

from eemeter.structures import (
    EnergyTrace,
    EnergyTraceSet,
    Intervention,
    ZIPCodeSite,
    Project as EEMeterProject,
)
from eemeter.io.serializers import ArbitraryStartSerializer
from eemeter.ee.meter import EnergyEfficiencyMeter
from eemeter import get_version

from warnings import warn
import numpy as np

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
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'Project {}'.format(self.project_id)

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
        return Intervention(self.baseline_period_end,
                            self.reporting_period_start)

    def _eemeter_location(self):
        return ZIPCodeSite(zipcode=self.zipcode)

    def run_meter(self, meter_class='EnergyEfficiencyMeter',
                  meter_settings=None, project_run=None,
                  weather_source=None, weather_normal_source=None):
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
        project_result : datastore.models.ProjectResult
            Object containing results of meter run.
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
        results = meter.evaluate(project, weather_source=weather_source,
                                 weather_normal_source=weather_normal_source)

        weather_source = results['weather_source']
        if weather_source is not None:
            weather_source_station = weather_source.station
        else:
            weather_source_station = None

        weather_normal_source = \
            results['weather_normal_source']
        if weather_normal_source is not None:
            weather_normal_source_station = weather_normal_source.station
        else:
            weather_normal_source_station = None

        project_result = ProjectResult.objects.create(
            project=self,
            project_run=project_run,
            eemeter_version=get_version(),
            meter_class=meter_class,
            meter_settings=meter_settings,
            weather_source_station=weather_source_station,
            weather_normal_source_station=weather_normal_source_station,
        )

        modeling_period_mapping = {}

        for modeling_period_label, modeling_period in \
                results['modeling_period_set'].iter_modeling_periods():
            mp = ModelingPeriod.objects.create(
                project_result=project_result,
                interpretation=modeling_period.interpretation,
                start_date=modeling_period.start_date,
                end_date=modeling_period.end_date,
            )
            modeling_period_mapping[modeling_period_label] = mp

        modeling_period_group_mapping = {}
        for (baseline_label, reporting_label), _ in \
                results['modeling_period_set'].iter_modeling_period_groups():
            mp_baseline = modeling_period_mapping[baseline_label]
            mp_reporting = modeling_period_mapping[reporting_label]
            mpg = ModelingPeriodGroup.objects.create(
                project_result=project_result,
                baseline_period=mp_baseline,
                reporting_period=mp_reporting,
            )
            modeling_period_group_mapping[
                (baseline_label, reporting_label)] = mpg

        # one result per trace per model
        energy_trace_model_result_mapping = {}
        for trace_label, modeled_energy_trace in \
                results['modeled_energy_traces'].items():
            for model_label, outputs in \
                    modeled_energy_trace.fit_outputs.items():

                trace = modeled_energy_trace.trace
                records_count = trace.data.shape[0]
                if records_count > 0:
                    records_start_date = trace.data.index[0]
                    records_end_date = trace.data.index[-1]
                else:
                    records_start_date = None
                    records_end_date = None

                etm = EnergyTraceModelResult.objects.create(
                    project_result=project_result,
                    energy_trace_id=trace_label,
                    modeling_period=modeling_period_mapping[model_label],
                    model_serializiation=None,
                    status=outputs['status'],
                    r2=outputs.get('r2'),
                    rmse=outputs.get('rmse'),
                    cvrmse=outputs.get('cvrmse'),
                    upper=outputs.get('upper'),
                    lower=outputs.get('lower'),
                    n=outputs.get('n'),
                    input_start_date=outputs.get('start_date'),
                    input_end_date=outputs.get('end_date'),
                    input_n_rows=outputs.get('n_rows'),
                    records_start_date=records_start_date,
                    records_end_date=records_end_date,
                    records_count=records_count,
                    traceback=outputs.get('traceback'),
                )
                energy_trace_model_result_mapping[
                    (trace_label, model_label)] = etm

        aggregation_interpretations = [
            'annualized_weather_normal',
            'gross_predicted',
        ]

        for trace_label, modeling_period_group_derivatives in \
                results['modeled_energy_trace_derivatives'].items():

            # get all modeling period derivatives
            modeling_period_derivatives = {}
            for (baseline_label, reporting_label), derivatives in \
                    modeling_period_group_derivatives.items():
                modeling_period_derivatives[baseline_label] = \
                    derivatives['BASELINE']
                modeling_period_derivatives[reporting_label] = \
                    derivatives['REPORTING']

            for modeling_period_label, derivatives in \
                    modeling_period_derivatives.items():

                for interpretation in aggregation_interpretations:

                    derivative = derivatives.get(interpretation, None)

                    energy_trace_model_res = \
                        energy_trace_model_result_mapping[
                            (trace_label, modeling_period_label)]

                    if derivative is not None:
                        Derivative.objects.create(
                            energy_trace_model_result=energy_trace_model_res,
                            interpretation=interpretation,
                            value=derivative[0],
                            upper=derivative[1],
                            lower=derivative[2],
                            n=derivative[3],
                        )

        # one result per aggregation - baseline + reporting?
        for group_label, group_derivatives in \
                results['project_derivatives'].items():
            for name, named_results in group_derivatives.items():
                if named_results is None:
                    continue

                for interpretation in aggregation_interpretations:

                    baseline_output = \
                        named_results['BASELINE'][interpretation]
                    reporting_output = \
                        named_results['REPORTING'][interpretation]

                    modeling_period_group = \
                        modeling_period_group_mapping[group_label]

                    DerivativeAggregation.objects.create(
                        project_result=project_result,
                        modeling_period_group=modeling_period_group,
                        trace_interpretation=name,
                        interpretation=interpretation,
                        baseline_value=baseline_output[0],
                        baseline_upper=baseline_output[1],
                        baseline_lower=baseline_output[2],
                        baseline_n=baseline_output[3],
                        reporting_value=reporting_output[0],
                        reporting_upper=reporting_output[1],
                        reporting_lower=reporting_output[2],
                        reporting_n=reporting_output[3],
                    )

        return project_result

    def _get_meter(self, meter_class, settings=None):
        MeterClass = METER_CLASS_CHOICES.get(meter_class, None)
        if MeterClass is None:
            raise ValueError("Received an invald meter_class %s" % meter_class)
        if settings is None:
            settings = {}
        meter = MeterClass(settings=settings)
        return meter

    def attributes(self):
        return self.projectattribute_set.all()


@python_2_unicode_compatible
class ProjectRun(models.Model):
    """ Encapsulates the request to run a Project's meters, pointing to
       Celery objects and Meter results.
    """
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
    status = models.CharField(max_length=250, choices=STATUS_CHOICES,
                              default="PENDING")
    meter_class = models.CharField(max_length=250, null=True,
                                   default="EnergyEfficiencyMeter")
    meter_settings = JSONField(null=True)
    traceback = models.CharField(max_length=10000, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            u'ProjectRun(project_id={}, status={})'
            .format(self.project.project_id, self.status)
        )


@python_2_unicode_compatible
class ProjectAttributeKey(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=25,
                                 choices=PROJECT_ATTRIBUTE_DATA_TYPE_CHOICES)

    def __str__(self):
        return (
            u'"{}" ({}, {})'
            .format(self.display_name, self.name, self.data_type)
        )


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
        return (
            u'({}, {}, project:{})'
            .format(self.key.name, self.value(), self.project)
        )


@python_2_unicode_compatible
class ProjectBlock(models.Model):
    name = models.CharField(max_length=255)
    projects = models.ManyToManyField(Project)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            u'(name={}, n_projects={})'
            .format(self.name, self.projects.count())
        )


@python_2_unicode_compatible
class ConsumptionMetadata(models.Model):
    interpretation = models.CharField(max_length=16,
                                      choices=INTERPRETATION_CHOICES)
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
        return (
            u'ConsumptionMetadata(interpretation={}, unit={}, n={})'
            .format(self.interpretation, self.unit, n)
        )


@python_2_unicode_compatible
class ConsumptionRecord(models.Model):
    metadata = models.ForeignKey(ConsumptionMetadata, related_name="records")
    start = models.DateTimeField()
    value = models.FloatField(blank=True, null=True)
    estimated = models.BooleanField()

    def __str__(self):
        return (
            u'Consumption(start={}, value={}, estimated={})'
            .format(self.start, self.value, self.estimated)
        )

    class Meta:
        ordering = ['start']

    def eemeter_record(self):
        return {
            "start": self.start,
            "value": self.value,
            "estimated": self.estimated
        }

    def value_clean(self):
        return _json_clean(self.value)


@python_2_unicode_compatible
class ProjectResult(models.Model):
    project = models.ForeignKey(Project, related_name='project_results')
    project_run = models.ForeignKey(ProjectRun, blank=True, null=True)
    eemeter_version = models.CharField(max_length=100)
    meter_class = models.CharField(max_length=250, blank=True, null=True)
    meter_settings = JSONField(null=True)
    weather_source_station = models.CharField(
        max_length=20, blank=True, null=True)
    weather_normal_source_station = models.CharField(
        max_length=20, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            u'ProjectResult(project_id={}, eemeter_version={},'
            ' meter_class={}, meter_settings={})'
            .format(self.project.project_id, self.eemeter_version,
                    self.meter_class, self.meter_settings)
        )


@python_2_unicode_compatible
class ModelingPeriod(models.Model):
    project_result = models.ForeignKey(ProjectResult,
                                       related_name='modeling_periods')
    interpretation = models.CharField(
        max_length=10,
        choices=(('BASELINE', 'Baseline'), ('REPORTING', 'Reporting'),)
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            u'ModelingPeriod(interpretation={}, start_date={}, end_date={})'
            .format(self.interpretation, self.start_date, self.end_date)
        )

    def clean(self):
        if self.interpretation == 'BASELINE' and self.end_date is None:
            raise ValidationError({
                'baseline_end_date':
                    'end_date cannot be null with interpretation BASELINE.'
            })

        if self.interpretation == 'REPORTING' and self.start_date is None:
            raise ValidationError({
                'reporting_start_date':
                    'start_date cannot be null with interpretation REPORTING.'
            })
        return True

    def n_days(self):
        if self.start_date is None or self.end_date is None:
            return np.inf
        else:
            return (self.end_date - self.start_date).days


@python_2_unicode_compatible
class ModelingPeriodGroup(models.Model):
    project_result = models.ForeignKey(ProjectResult,
                                       related_name='modeling_period_groups')

    # TODO: validate consistency of these
    baseline_period = models.ForeignKey(ModelingPeriod,
                                        related_name='baseline_groups')
    reporting_period = models.ForeignKey(ModelingPeriod,
                                         related_name='reporting_groups')

    def __str__(self):
        return (
            u'ModelingPeriodGroup(baseline_period={}, reporting_period={})'
            .format(self.baseline_period, self.reporting_period)
        )

    def clean(self):
        if self.baseline_period.interpretation != 'BASELINE':
            raise ValidationError({
                'baseline_period':
                    'Baseline period must have interpretation BASELINE.'
            })

        if self.reporting_period.interpretation != 'REPORTING':
            raise ValidationError({
                'reporting_period':
                    'Reporting period must have interpretation REPORTING.'
            })

        if self.baseline_period.end_date > self.reporting_period.start_date:
            raise ValidationError({
                'periods':
                    'Reporting period must start after baseline period ends.'
            })

        return True

    def n_gap_days(self):
        gap = self.reporting_period.start_date - self.baseline_period.end_date
        return gap.days


@python_2_unicode_compatible
class EnergyTraceModelResult(models.Model):
    project_result = models.ForeignKey(
        ProjectResult, related_name='energy_trace_model_results')
    energy_trace = models.ForeignKey(ConsumptionMetadata)
    modeling_period = models.ForeignKey(ModelingPeriod)
    status = models.CharField(max_length=1000, null=True)
    r2 = models.FloatField(null=True, blank=True)
    rmse = models.FloatField(null=True, blank=True)
    cvrmse = models.FloatField(null=True, blank=True)
    model_serializiation = models.CharField(max_length=10000, null=True,
                                            blank=True)
    upper = models.FloatField(null=True, blank=True)
    lower = models.FloatField(null=True, blank=True)
    n = models.FloatField(null=True, blank=True)
    input_start_date = models.DateTimeField(null=True, blank=True)
    input_end_date = models.DateTimeField(null=True, blank=True)
    input_n_rows = models.IntegerField(null=True, blank=True)
    records_start_date = models.DateTimeField(null=True, blank=True)
    records_end_date = models.DateTimeField(null=True, blank=True)
    records_count = models.IntegerField(null=True, blank=True)
    traceback = models.CharField(max_length=10000, null=True, blank=True)

    def __str__(self):
        return (
            u'EnergyTraceModelResult(status={}, r2={}, cvrmse={})'
            .format(self.status, self.r2, self.cvrmse)
        )


@python_2_unicode_compatible
class Derivative(models.Model):
    energy_trace_model_result = models.ForeignKey(EnergyTraceModelResult,
                                                  related_name='derivatives')
    interpretation = models.CharField(max_length=100)
    value = models.FloatField()
    upper = models.FloatField()
    lower = models.FloatField()
    n = models.IntegerField()

    def __str__(self):
        return (
            u'Derivative(interpretation={}, value={}, upper={}, lower={})'
            .format(self.interpretation, self.value, self.upper, self.lower)
        )


@python_2_unicode_compatible
class DerivativeAggregation(models.Model):
    project_result = models.ForeignKey(
        ProjectResult, related_name='derivative_aggregations')
    modeling_period_group = models.ForeignKey(
        ModelingPeriodGroup, related_name='derivative_aggregations')
    trace_interpretation = models.CharField(max_length=100)
    interpretation = models.CharField(max_length=100)
    baseline_value = models.FloatField()
    baseline_upper = models.FloatField()
    baseline_lower = models.FloatField()
    baseline_n = models.IntegerField()
    reporting_value = models.FloatField()
    reporting_upper = models.FloatField()
    reporting_lower = models.FloatField()
    reporting_n = models.IntegerField()

    def __str__(self):
        return (
            u'Aggregation(trace_interpretation={}, interpretation={}, '
            'baseline_value={}, reporting_value={})'
            .format(self.trace_interpretation, self.interpretation,
                    self.baseline_value, self.reporting_value)
        )


@receiver(post_save, sender=User)
def create_project_owner(sender, instance, **kwargs):
    project_owner, created = ProjectOwner.objects.get_or_create(user=instance)
