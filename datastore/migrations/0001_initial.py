# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsumptionMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fuel_type', models.CharField(max_length=3, choices=[(b'E', b'electricity'), (b'NG', b'natural_gas')])),
                ('energy_unit', models.CharField(max_length=3, choices=[(b'KWH', b'kWh'), (b'THM', b'therm')])),
            ],
        ),
        migrations.CreateModel(
            name='ConsumptionRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('value', models.FloatField(null=True, blank=True)),
                ('estimated', models.BooleanField()),
                ('metadata', models.ForeignKey(related_name='records', to='datastore.ConsumptionMetadata')),
            ],
            options={
                'ordering': ['start'],
            },
        ),
        migrations.CreateModel(
            name='DailyUsageBaseline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='DailyUsageReporting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='MeterRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serialization', models.CharField(max_length=100000, null=True, blank=True)),
                ('annual_usage_baseline', models.FloatField(null=True, blank=True)),
                ('annual_usage_reporting', models.FloatField(null=True, blank=True)),
                ('gross_savings', models.FloatField(null=True, blank=True)),
                ('annual_savings', models.FloatField(null=True, blank=True)),
                ('model_type', models.CharField(blank=True, max_length=250, null=True, choices=[(b'DFLT_RES_E', b'Default Residential Electricity'), (b'DFLT_RES_NG', b'Default Residential Natural Gas'), (b'DFLT_COM_E', b'Default Commercial Electricity'), (b'DFLT_COM_NG', b'Default Commercial Natural Gas')])),
                ('model_parameter_json', models.CharField(max_length=10000, null=True, blank=True)),
                ('consumption_metadata', models.ForeignKey(to='datastore.ConsumptionMetadata')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_id', models.CharField(max_length=255)),
                ('baseline_period_start', models.DateTimeField(null=True, blank=True)),
                ('baseline_period_end', models.DateTimeField(null=True, blank=True)),
                ('reporting_period_start', models.DateTimeField(null=True, blank=True)),
                ('reporting_period_end', models.DateTimeField(null=True, blank=True)),
                ('zipcode', models.CharField(max_length=10, null=True, blank=True)),
                ('weather_station', models.CharField(max_length=10, null=True, blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('project', models.ManyToManyField(to='datastore.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='project_owner',
            field=models.ForeignKey(to='datastore.ProjectOwner'),
        ),
        migrations.AddField(
            model_name='meterrun',
            name='project',
            field=models.ForeignKey(to='datastore.Project'),
        ),
        migrations.AddField(
            model_name='dailyusagereporting',
            name='meter_run',
            field=models.ForeignKey(to='datastore.MeterRun'),
        ),
        migrations.AddField(
            model_name='dailyusagebaseline',
            name='meter_run',
            field=models.ForeignKey(to='datastore.MeterRun'),
        ),
        migrations.AddField(
            model_name='consumptionmetadata',
            name='project',
            field=models.ForeignKey(blank=True, to='datastore.Project', null=True),
        ),
    ]
