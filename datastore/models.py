from django.db import models
from django.contrib.auth.models import User

class ProjectOwner(models.Model):
    user = models.OneToOneField(User)

class Project(models.Model):
    project_owner = models.ForeignKey(ProjectOwner)
    project_id = models.CharField(max_length=255)

class Block(models.Model):
    name = models.CharField(max_length=255)
    project = models.ManyToManyField(Project)

class ConsumptionMetadata(models.Model):
    FUEL_TYPE_CHOICES = (
        ('E', 'electricity'),
        ('NG', 'natural_gas'),
    )
    FUEL_UNIT_CHOICES = (
        ('KWH', 'kilowatthours'),
        ('THM', 'therms'),
    )
    fuel_type = models.CharField(max_length=3, choices=FUEL_TYPE_CHOICES)
    fuel_unit = models.CharField(max_length=3, choices=FUEL_UNIT_CHOICES)
    project = models.ForeignKey(Project, blank=True, null=True)

class ConsumptionRecord(models.Model):
    metadata = models.ForeignKey(ConsumptionMetadata, related_name="records")
    start = models.DateTimeField()
    value = models.FloatField(blank=True, null=True)
    estimated = models.BooleanField()

    class Meta:
        ordering = ['start']

class MeterRun(models.Model):
    project = models.ForeignKey(Project)
    consumption_metadata_id = models.ForeignKey(ConsumptionMetadata)
    serialization = models.CharField(max_length=100000)

class DailyUsageBaseline(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

class DailyUsageReporting(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()
    date = models.DateField()

class AnnualUsageBaseline(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()

class AnnualUsageReporting(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()

class GrossSavings(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()

class AnnualSavings(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    value = models.FloatField()

class ModelType(models.Model):
    model_name = models.CharField(max_length=255)

class ModelParameters(models.Model):
    meter_run = models.ForeignKey(MeterRun)
    model_type = models.ForeignKey(ModelType)
    parameters_json = models.CharField(max_length=255)
