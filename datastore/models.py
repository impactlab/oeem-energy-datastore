from django.db import models
from django.contrib.auth.models import User

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

class ProjectBlock(models.Model):
    name = models.CharField(max_length=255)
    project = models.ManyToManyField(Project)

class ConsumptionMetadata(models.Model):
    FUEL_TYPE_CHOICES = (
        ('E', 'electricity'),
        ('NG', 'natural_gas'),
    )
    ENERGY_UNIT_CHOICES = (
        ('KWH', 'kilowatthours'),
        ('THM', 'therms'),
    )
    fuel_type = models.CharField(max_length=3, choices=FUEL_TYPE_CHOICES)
    energy_unit = models.CharField(max_length=3, choices=ENERGY_UNIT_CHOICES)
    project = models.ForeignKey(Project, blank=True, null=True)

class ConsumptionRecord(models.Model):
    metadata = models.ForeignKey(ConsumptionMetadata, related_name="records")
    start = models.DateTimeField()
    value = models.FloatField(blank=True, null=True)
    estimated = models.BooleanField()

    class Meta:
        ordering = ['start']

class MeterRun(models.Model):
    MODEL_TYPE_CHOICES = (
        ('DFLT_RES_E', 'Default Residential Electricity'),
        ('DFLT_RES_NG', 'Default Residential Natural Gas'),
        ('DFLT_COM_E', 'Default Commercial Electricity'),
        ('DFLT_COM_NG', 'Default Commercial Natural Gas'),
    )
    project = models.ForeignKey(Project)
    consumption_metadata_id = models.ForeignKey(ConsumptionMetadata)
    serialization = models.CharField(max_length=100000)
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
