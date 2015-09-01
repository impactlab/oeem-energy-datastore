from django.db import models

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

class ConsumptionRecord(models.Model):
    metadata = models.ForeignKey(ConsumptionMetadata, related_name="records")
    start = models.DateTimeField()
    value = models.FloatField(null=True, blank=True)
    estimated = models.BooleanField()

    class Meta:
        ordering = ['start']
