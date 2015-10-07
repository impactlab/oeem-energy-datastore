# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0011_auto_20151006_2036'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyUsageSummaryActual',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='MonthlyUsageSummaryBaseline',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='MonthlyUsageSummaryReporting',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.RemoveField(
            model_name='monthlyaverageusagesummaryactual',
            name='fuel_type_summary',
        ),
        migrations.RemoveField(
            model_name='monthlyaverageusagesummarybaseline',
            name='fuel_type_summary',
        ),
        migrations.RemoveField(
            model_name='monthlyaverageusagesummaryreporting',
            name='fuel_type_summary',
        ),
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='fuel_type',
            field=models.CharField(choices=[('E', 'electricity'), ('NG', 'natural_gas')], max_length=3),
        ),
        migrations.AlterField(
            model_name='fueltypesummary',
            name='fuel_type',
            field=models.CharField(choices=[('E', 'electricity'), ('NG', 'natural_gas')], max_length=3),
        ),
        migrations.DeleteModel(
            name='MonthlyAverageUsageSummaryActual',
        ),
        migrations.DeleteModel(
            name='MonthlyAverageUsageSummaryBaseline',
        ),
        migrations.DeleteModel(
            name='MonthlyAverageUsageSummaryReporting',
        ),
        migrations.AddField(
            model_name='monthlyusagesummaryreporting',
            name='fuel_type_summary',
            field=models.ForeignKey(to='datastore.FuelTypeSummary'),
        ),
        migrations.AddField(
            model_name='monthlyusagesummarybaseline',
            name='fuel_type_summary',
            field=models.ForeignKey(to='datastore.FuelTypeSummary'),
        ),
        migrations.AddField(
            model_name='monthlyusagesummaryactual',
            name='fuel_type_summary',
            field=models.ForeignKey(to='datastore.FuelTypeSummary'),
        ),
    ]
