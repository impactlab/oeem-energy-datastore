from django.db import models
from django.contrib.auth.models import User
from eemeter.evaluation import Period
from eemeter.project import Project as EEMeterProject
from eemeter.consumption import ConsumptionData as EEMeterConsumptionData
from eemeter.location import Location
from warnings import warn

class ProjectOwner(models.Model):
    user = models.OneToOneField(User)

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

    def run_meter(self, model_type='residential'):
        try:
            project, cm_ids = self.eemeter_project()
        except ValueError:
            message = "Cannot create eemeter project; skipping project id={}.".format(self.project_id)
            warn(message)

        for consumption_data, cm_id in zip(project.consumption, cm_ids):

            # determine model type
            model_type_str = None
            if model_type == "residential":
                if consumption_data.fuel_type == "electricity":
                    model_type_str = "DFLT_RES_E"
                elif consumption_data.fuel_type == "natural_gas":
                    model_type_str = "DFLT_RES_NG"
            elif model_type == "commercial":
                if consumption_data.fuel_type == "electricity":
                    model_type_str = "DFLT_COM_E"
                elif consumption_data.fuel_type == "natural_gas":
                    model_type_str = "DFLT_COM_NG"

            meter_run = MeterRun(project=self,
                    consumption_metadata_id=ConsumptionMetadata.objects.get(pk=cm_id),
                    model_type=model_type_str)
            meter_run.save()

class ProjectBlock(models.Model):
    name = models.CharField(max_length=255)
    project = models.ManyToManyField(Project)

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


class ConsumptionRecord(models.Model):
    metadata = models.ForeignKey(ConsumptionMetadata, related_name="records")
    start = models.DateTimeField()
    value = models.FloatField(blank=True, null=True)
    estimated = models.BooleanField()

    class Meta:
        ordering = ['start']

    def eemeter_record(self):
        return {"start": self.start, "value": self.value, "estimated": self.estimated }

class MeterRun(models.Model):
    MODEL_TYPE_CHOICES = (
        ('DFLT_RES_E', 'Default Residential Electricity'),
        ('DFLT_RES_NG', 'Default Residential Natural Gas'),
        ('DFLT_COM_E', 'Default Commercial Electricity'),
        ('DFLT_COM_NG', 'Default Commercial Natural Gas'),
    )
    project = models.ForeignKey(Project)
    consumption_metadata_id = models.ForeignKey(ConsumptionMetadata)
    serialization = models.CharField(max_length=100000, blank=True, null=True)
    annual_usage_baseline = models.FloatField(blank=True, null=True)
    annual_usage_reporting = models.FloatField(blank=True, null=True)
    gross_savings = models.FloatField(blank=True, null=True)
    annual_savings = models.FloatField(blank=True, null=True)
    model_type = models.CharField(max_length=250, choices=MODEL_TYPE_CHOICES, blank=True, null=True)
    model_parameter_json = models.CharField(max_length=10000, blank=True, null=True)

class DailyUsageBaseline(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

class DailyUsageReporting(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()
