# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0005_auto_20150915_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumptionmetadata',
            name='added',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 4, 855088, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='consumptionmetadata',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 9, 86897, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meterrun',
            name='added',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 11, 710956, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meterrun',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 14, 351118, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='added',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 16, 694589, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 21, 230717, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projectblock',
            name='added',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 23, 662893, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projectblock',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 25, 806574, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projectowner',
            name='added',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 28, 454558, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projectowner',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 15, 20, 46, 30, 558739, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='energy_unit',
            field=models.CharField(choices=[('THM', 'therm'), ('KWH', 'kWh')], max_length=3),
        ),
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='fuel_type',
            field=models.CharField(choices=[('E', 'electricity'), ('NG', 'natural_gas')], max_length=3),
        ),
    ]
