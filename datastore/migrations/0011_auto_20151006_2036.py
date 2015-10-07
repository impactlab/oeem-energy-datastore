# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0010_auto_20151006_1954'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyUsageSummaryActual',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='DailyUsageSummaryBaseline',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='DailyUsageSummaryReporting',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='FuelTypeSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('fuel_type', models.CharField(choices=[('NG', 'natural_gas'), ('E', 'electricity')], max_length=3)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('project_block', models.ForeignKey(to='datastore.ProjectBlock')),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyAverageUsageSummaryActual',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
                ('fuel_type_summary', models.ForeignKey(to='datastore.FuelTypeSummary')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='MonthlyAverageUsageSummaryBaseline',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
                ('fuel_type_summary', models.ForeignKey(to='datastore.FuelTypeSummary')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='MonthlyAverageUsageSummaryReporting',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
                ('fuel_type_summary', models.ForeignKey(to='datastore.FuelTypeSummary')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.RemoveField(
            model_name='dailyusageactualprojectblock',
            name='project_block',
        ),
        migrations.RemoveField(
            model_name='dailyusagebaselineprojectblock',
            name='project_block',
        ),
        migrations.RemoveField(
            model_name='dailyusagereportingprojectblock',
            name='project_block',
        ),
        migrations.RemoveField(
            model_name='monthlyaverageusageactualprojectblock',
            name='project_block',
        ),
        migrations.RemoveField(
            model_name='monthlyaverageusagebaselineprojectblock',
            name='project_block',
        ),
        migrations.RemoveField(
            model_name='monthlyaverageusagereportingprojectblock',
            name='project_block',
        ),
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
        migrations.DeleteModel(
            name='DailyUsageActualProjectBlock',
        ),
        migrations.DeleteModel(
            name='DailyUsageBaselineProjectBlock',
        ),
        migrations.DeleteModel(
            name='DailyUsageReportingProjectBlock',
        ),
        migrations.DeleteModel(
            name='MonthlyAverageUsageActualProjectBlock',
        ),
        migrations.DeleteModel(
            name='MonthlyAverageUsageBaselineProjectBlock',
        ),
        migrations.DeleteModel(
            name='MonthlyAverageUsageReportingProjectBlock',
        ),
        migrations.AddField(
            model_name='dailyusagesummaryreporting',
            name='fuel_type_summary',
            field=models.ForeignKey(to='datastore.FuelTypeSummary'),
        ),
        migrations.AddField(
            model_name='dailyusagesummarybaseline',
            name='fuel_type_summary',
            field=models.ForeignKey(to='datastore.FuelTypeSummary'),
        ),
        migrations.AddField(
            model_name='dailyusagesummaryactual',
            name='fuel_type_summary',
            field=models.ForeignKey(to='datastore.FuelTypeSummary'),
        ),
    ]
