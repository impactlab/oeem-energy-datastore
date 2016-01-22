# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0015_auto_20160122_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='energy_unit',
            field=models.CharField(max_length=3, choices=[('KWH', 'kWh'), ('THM', 'therm')]),
        ),
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='fuel_type',
            field=models.CharField(max_length=3, choices=[('E', 'electricity'), ('NG', 'natural_gas')]),
        ),
        migrations.AlterField(
            model_name='fueltypesummary',
            name='fuel_type',
            field=models.CharField(max_length=3, choices=[('E', 'electricity'), ('NG', 'natural_gas')]),
        ),
        migrations.AlterField(
            model_name='projectattributekey',
            name='data_type',
            field=models.CharField(max_length=25, choices=[('CHAR', 'char_value'), ('FLOAT', 'float_value'), ('DATE', 'date_value')]),
        ),
    ]
