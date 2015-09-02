# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0003_auto_20150902_1545'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='baseline_period',
        ),
        migrations.RemoveField(
            model_name='project',
            name='reporting_period',
        ),
        migrations.AddField(
            model_name='project',
            name='baseline_period_end',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='baseline_period_start',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='reporting_period_end',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='reporting_period_start',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='Period',
        ),
    ]
