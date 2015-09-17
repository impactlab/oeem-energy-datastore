# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0007_auto_20150917_1702'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyAverageUsageBaseline',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('value', models.FloatField()),
                ('date', models.DateField()),
                ('meter_run', models.ForeignKey(to='datastore.MeterRun')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='MonthlyAverageUsageReporting',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('value', models.FloatField()),
                ('date', models.DateField()),
                ('meter_run', models.ForeignKey(to='datastore.MeterRun')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='energy_unit',
            field=models.CharField(max_length=3, choices=[('KWH', 'kWh'), ('THM', 'therm')]),
        ),
    ]
