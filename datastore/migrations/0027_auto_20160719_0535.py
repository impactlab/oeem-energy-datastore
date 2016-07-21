# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-19 05:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0026_auto_20160718_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='derivative',
            name='energy_trace_model_result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='derivatives', to='datastore.EnergyTraceModelResult'),
        ),
        migrations.AlterField(
            model_name='derivativeaggregation',
            name='modeling_period_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='derivative_aggregations', to='datastore.ModelingPeriodGroup'),
        ),
        migrations.AlterField(
            model_name='derivativeaggregation',
            name='project_result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='derivative_aggregations', to='datastore.ProjectResult'),
        ),
        migrations.AlterField(
            model_name='energytracemodelresult',
            name='project_result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='energy_trace_model_results', to='datastore.ProjectResult'),
        ),
        migrations.AlterField(
            model_name='modelingperiod',
            name='project_result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modeling_periods', to='datastore.ProjectResult'),
        ),
        migrations.AlterField(
            model_name='modelingperiodgroup',
            name='baseline_period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='baseline_groups', to='datastore.ModelingPeriod'),
        ),
        migrations.AlterField(
            model_name='modelingperiodgroup',
            name='project_result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modeling_period_groups', to='datastore.ProjectResult'),
        ),
        migrations.AlterField(
            model_name='modelingperiodgroup',
            name='reporting_period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reporting_groups', to='datastore.ModelingPeriod'),
        ),
        migrations.AlterField(
            model_name='projectresult',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_result', to='datastore.Project'),
        ),
    ]
