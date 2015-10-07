# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0009_auto_20151005_1932'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyUsageActualProjectBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('fuel_type', models.CharField(choices=[('E', 'electricity'), ('NG', 'natural_gas')], max_length=3)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
                ('project_block', models.ForeignKey(to='datastore.ProjectBlock')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='MonthlyAverageUsageActualProjectBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('fuel_type', models.CharField(choices=[('E', 'electricity'), ('NG', 'natural_gas')], max_length=3)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
                ('project_block', models.ForeignKey(to='datastore.ProjectBlock')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='energy_unit',
            field=models.CharField(choices=[('THM', 'therm'), ('KWH', 'kWh')], max_length=3),
        ),
    ]
