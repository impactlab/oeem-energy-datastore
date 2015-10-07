# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0008_auto_20150917_2219'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyUsageBaselineProjectBlock',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
            name='DailyUsageReportingProjectBlock',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
            name='MonthlyAverageUsageBaselineProjectBlock',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
            name='MonthlyAverageUsageReportingProjectBlock',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
            name='fuel_type',
            field=models.CharField(choices=[('E', 'electricity'), ('NG', 'natural_gas')], max_length=3),
        ),
    ]
