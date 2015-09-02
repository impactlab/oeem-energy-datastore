# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0004_auto_20150902_2001'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Block',
            new_name='ProjectBlock',
        ),
        migrations.RemoveField(
            model_name='annualsavings',
            name='meter_run',
        ),
        migrations.RemoveField(
            model_name='annualusagebaseline',
            name='meter_run',
        ),
        migrations.RemoveField(
            model_name='annualusagereporting',
            name='meter_run',
        ),
        migrations.RemoveField(
            model_name='grosssavings',
            name='meter_run',
        ),
        migrations.RemoveField(
            model_name='modelparameters',
            name='meter_run',
        ),
        migrations.RemoveField(
            model_name='modelparameters',
            name='model_type',
        ),
        migrations.AddField(
            model_name='meterrun',
            name='annual_savings',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='meterrun',
            name='annual_usage_baseline',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='meterrun',
            name='annual_usage_reporting',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='meterrun',
            name='gross_savings',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='meterrun',
            name='model_parameter_json',
            field=models.CharField(max_length=10000, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='meterrun',
            name='model_type',
            field=models.CharField(blank=True, max_length=250, null=True, choices=[(b'DFLT_RES_E', b'Default Residential Electricity'), (b'DFLT_RES_NG', b'Default Residential Natural Gas'), (b'DFLT_COM_E', b'Default Commercial Electricity'), (b'DFLT_COM_NG', b'Default Commercial Natural Gas')]),
        ),
        migrations.DeleteModel(
            name='AnnualSavings',
        ),
        migrations.DeleteModel(
            name='AnnualUsageBaseline',
        ),
        migrations.DeleteModel(
            name='AnnualUsageReporting',
        ),
        migrations.DeleteModel(
            name='GrossSavings',
        ),
        migrations.DeleteModel(
            name='ModelParameters',
        ),
        migrations.DeleteModel(
            name='ModelType',
        ),
    ]
