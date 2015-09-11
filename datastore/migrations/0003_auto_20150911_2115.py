# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0002_auto_20150910_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='energy_unit',
            field=models.CharField(choices=[('KWH', 'kWh'), ('THM', 'therm')], max_length=3),
        ),
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='fuel_type',
            field=models.CharField(choices=[('NG', 'natural_gas'), ('E', 'electricity')], max_length=3),
        ),
        migrations.AlterField(
            model_name='meterrun',
            name='model_type',
            field=models.CharField(null=True, blank=True, choices=[('DFLT_RES_E', 'Default Residential Electricity'), ('DFLT_RES_NG', 'Default Residential Natural Gas'), ('DFLT_COM_E', 'Default Commercial Electricity'), ('DFLT_COM_NG', 'Default Commercial Natural Gas')], max_length=250),
        ),
    ]
