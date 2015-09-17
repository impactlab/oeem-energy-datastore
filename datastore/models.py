from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.encoding import python_2_unicode_compatible

from eemeter.evaluation import Period
from eemeter.project import Project as EEMeterProject
from eemeter.consumption import ConsumptionData as EEMeterConsumptionData
from eemeter.location import Location
from eemeter.meter import DataCollection
from eemeter.meter import DefaultResidentialMeter
from eemeter.config.yaml_parser import dump
from eemeter.models.temperature_sensitivity import AverageDailyTemperatureSensitivityModel

from warnings import warn
from datetime import timedelta
import numpy as np
import json

class ProjectOwner(models.Model):
    user = models.OneToOneField(User)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @python_2_unicode_compatible
    def __str__(self):
        return u'ProjectOwner {}'.format(self.user.username)

class Project(models.Model):
    project_owner = models.ForeignKey(ProjectOwner)
    project_id = models.CharField(max_length=255)
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

    @python_2_unicode_compatible
    def __str__(self):
        return u'Project {}'.format(self.project_id)

    @property
    def baseline_period(self):
        return Period(self.baseline_period_start, self.baseline_period_end)

    @property
    def reporting_period(self):
        return Period(self.reporting_period_start, self.reporting_period_end)

    @property
    def lat_lng(self):
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        else:
            return None

    def eemeter_project(self):
        if self.lat_lng is not None:
            location = Location(lat_lng=self.lat_lng)
        elif self.weather_station is not None:
            location = Location(station=self.weather_station)
        else:
            location = Location(zipcode=self.zipcode)
        consumption = [cm.eemeter_consumption_data() for cm in self.consumptionmetadata_set.all()]
        consumption_metadata_ids = [cm.id for cm in self.consumptionmetadata_set.all()]

        project = EEMeterProject(location, consumption, self.baseline_period, self.reporting_period)
        return project, consumption_metadata_ids

    def run_meter(self, meter_type='residential', start_date=None, end_date=None, n_days=None):
        try:
            project, cm_ids = self.eemeter_project()
        except ValueError:
            message = "Cannot create eemeter project; skipping project id={}.".format(self.project_id)
            warn(message)

        if meter_type == "residential":
            meter = DefaultResidentialMeter()
        elif meter_type == "commercial":
            raise NotImplementedError
        else:
            raise NotImplementedError

        if start_date is None:
            start_date = now()
            for consumption_data in project.consumption:
                earliest_date = consumption_data.data.index[0].to_datetime()
                if earliest_date < start_date:
                    start_date = earliest_date

        if end_date is None:
            end_date = now()

        daily_evaluation_period = Period(start_date, end_date)

        meter_results = meter.evaluate(DataCollection(project=project))

        meter_runs = []
        for consumption_data, cm_id in zip(project.consumption, cm_ids):

            fuel_type_tag = consumption_data.fuel_type

            # determine model type
            if fuel_type_tag == "electricity":
                meter_type_suffix = "E"
                model = AverageDailyTemperatureSensitivityModel(heating=True,cooling=True)
            elif fuel_type_tag == "natural_gas":
                meter_type_suffix = "NG"
                model = AverageDailyTemperatureSensitivityModel(heating=True,cooling=False)
            else:
                raise NotImplementedError

            if meter_type == "residential":
                meter_type_str = "DFLT_RES_" + meter_type_suffix
            elif model_type == "commercial":
                meter_type_str = "DFLT_COM_" + meter_type_suffix

            # gather meter results
            annual_usage_baseline = meter_results.get_data("annualized_usage", ["baseline", fuel_type_tag])
            if annual_usage_baseline is not None:
                annual_usage_baseline = annual_usage_baseline.value

            annual_usage_reporting = meter_results.get_data("annualized_usage", ["reporting", fuel_type_tag])
            if annual_usage_reporting is not None:
                annual_usage_reporting = annual_usage_reporting.value

            gross_savings = meter_results.get_data("gross_savings", [fuel_type_tag])
            if gross_savings is not None:
                gross_savings = gross_savings.value

            annual_savings = None
            if annual_usage_baseline is not None and annual_usage_reporting is not None:
                annual_savings = annual_usage_baseline - annual_usage_reporting

            # gather meter results
            cvrmse_baseline = meter_results.get_data("cvrmse", ["baseline", fuel_type_tag])
            if cvrmse_baseline is not None:
                cvrmse_baseline = cvrmse_baseline.value

            cvrmse_reporting = meter_results.get_data("cvrmse", ["reporting", fuel_type_tag])
            if cvrmse_reporting is not None:
                cvrmse_reporting = cvrmse_reporting.value

            model_parameter_json_baseline = meter_results.get_data("model_params", ["baseline", fuel_type_tag])
            model_parameter_array_baseline = None
            if model_parameter_json_baseline is not None:
                model_parameter_dict_baseline = model_parameter_json_baseline.value.to_dict()
                model_parameter_json_baseline = json.dumps(model_parameter_dict_baseline)
                model_parameters_baseline = model.param_type(model_parameter_dict_baseline)

            model_parameter_json_reporting = meter_results.get_data("model_params", ["reporting", fuel_type_tag])
            model_parameter_array_reporting = None
            if model_parameter_json_reporting is not None:
                model_parameter_dict_reporting = model_parameter_json_reporting.value.to_dict()
                model_parameter_json_reporting = json.dumps(model_parameter_dict_reporting)
                model_parameters_reporting = model.param_type(model_parameter_dict_reporting)

            meter_run = MeterRun(project=self,
                    consumption_metadata=ConsumptionMetadata.objects.get(pk=cm_id),
                    serialization=dump(meter.meter),
                    annual_usage_baseline=annual_usage_baseline,
                    annual_usage_reporting=annual_usage_reporting,
                    gross_savings=gross_savings,
                    annual_savings=annual_savings,
                    meter_type=meter_type_str,
                    model_parameter_json_baseline=model_parameter_json_baseline,
                    model_parameter_json_reporting=model_parameter_json_reporting,
                    cvrmse_baseline=cvrmse_baseline,
                    cvrmse_reporting=cvrmse_reporting)

            meter_run.save()
            meter_runs.append(meter_run)

            # record time series of usage for baseline and reporting
            avg_temps = project.weather_source.daily_temperatures(
                    daily_evaluation_period, meter.temperature_unit_str)

            values_baseline = model.transform(avg_temps, model_parameters_baseline)
            values_reporting = model.transform(avg_temps, model_parameters_reporting)

            for value_baseline, value_reporting, days in zip(values_baseline, values_reporting, range(daily_evaluation_period.timedelta.days)):
                date = daily_evaluation_period.start + timedelta(days=days)

                daily_usage_baseline = DailyUsageBaseline(meter_run=meter_run, value=value_baseline, date=date)
                daily_usage_baseline.save()

                daily_usage_reporting = DailyUsageReporting(meter_run=meter_run, value=value_reporting, date=date)
                daily_usage_reporting.save()

        return meter_runs

    def recent_meter_runs(self):
        return [c.meterrun_set.latest('added') for c in self.consumptionmetadata_set.all()]

class ProjectBlock(models.Model):
    name = models.CharField(max_length=255)
    project_owner = models.ForeignKey(ProjectOwner)
    project = models.ManyToManyField(Project)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @python_2_unicode_compatible
    def __str__(self):
        return u'ProjectBlock {}'.format(self.name)

class ConsumptionMetadata(models.Model):
    FUEL_TYPE_CHOICES = {
            'E': 'electricity',
            'NG': 'natural_gas',
            }
    ENERGY_UNIT_CHOICES = {
            'KWH': 'kWh',
            'THM': 'therm',
            }

    fuel_type = models.CharField(max_length=3, choices=FUEL_TYPE_CHOICES.items())
    energy_unit = models.CharField(max_length=3, choices=ENERGY_UNIT_CHOICES.items())
    project = models.ForeignKey(Project, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def eemeter_consumption_data(self):
        FUEL_TYPE_CHOICES = {
                'E': 'electricity',
                'NG': 'natural_gas',
                }
        ENERGY_UNIT_CHOICES = {
                'KWH': 'kWh',
                'THM': 'therm',
                }
        records = self.records.all()
        records = [r.eemeter_record() for r in records]
        fuel_type = FUEL_TYPE_CHOICES[self.fuel_type]
        unit_name = ENERGY_UNIT_CHOICES[self.energy_unit]
        consumption_data = EEMeterConsumptionData(records, fuel_type=fuel_type,
                unit_name=unit_name, record_type="arbitrary_start")
        return consumption_data

    @python_2_unicode_compatible
    def __str__(self):
        n = len(self.records.all())
        return u'ConsumptionMetadata(fuel_type={}, energy_unit={}, n={})'.format(self.fuel_type, self.energy_unit, n)


class ConsumptionRecord(models.Model):
    metadata = models.ForeignKey(ConsumptionMetadata, related_name="records")
    start = models.DateTimeField()
    value = models.FloatField(blank=True, null=True)
    estimated = models.BooleanField()

    @python_2_unicode_compatible
    def __str__(self):
        return u'Consumption(start={}, value={}, estimated={})'.format(self.start, self.value, self.estimated)

    class Meta:
        ordering = ['start']

    def eemeter_record(self):
        return {"start": self.start, "value": self.value, "estimated": self.estimated }

class MeterRun(models.Model):
    METER_TYPE_CHOICES = (
        ('DFLT_RES_E', 'Default Residential Electricity'),
        ('DFLT_RES_NG', 'Default Residential Natural Gas'),
        ('DFLT_COM_E', 'Default Commercial Electricity'),
        ('DFLT_COM_NG', 'Default Commercial Natural Gas'),
    )
    project = models.ForeignKey(Project)
    consumption_metadata = models.ForeignKey(ConsumptionMetadata)
    serialization = models.CharField(max_length=100000, blank=True, null=True)
    annual_usage_baseline = models.FloatField(blank=True, null=True)
    annual_usage_reporting = models.FloatField(blank=True, null=True)
    gross_savings = models.FloatField(blank=True, null=True)
    annual_savings = models.FloatField(blank=True, null=True)
    meter_type = models.CharField(max_length=250, choices=METER_TYPE_CHOICES, blank=True, null=True)
    model_parameter_json_baseline = models.CharField(max_length=10000, blank=True, null=True)
    model_parameter_json_reporting = models.CharField(max_length=10000, blank=True, null=True)
    cvrmse_baseline = models.FloatField(blank=True, null=True)
    cvrmse_reporting = models.FloatField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @python_2_unicode_compatible
    def __str__(self):
        return u'MeterRun(project_id={}, valid={})'.format(self.project.project_id, self.valid_meter_run())

    def valid_meter_run(self, threshold=20):
        if self.cvrmse_baseline is None or self.cvrmse_reporting is None:
            return False
        return self.cvrmse_baseline < threshold and self.cvrmse_reporting < threshold

class DailyUsageBaseline(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    @python_2_unicode_compatible
    def __str__(self):
        return u'DailyUsageBaseline(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']

class DailyUsageReporting(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

    @python_2_unicode_compatible
    def __str__(self):
        return u'DailyUsageReporting(date={}, value={})'.format(self.date, self.value)

    class Meta:
        ordering = ['date']
