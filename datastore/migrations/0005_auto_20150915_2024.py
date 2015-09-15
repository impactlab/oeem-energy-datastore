# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0004_auto_20150914_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='meterrun',
            name='cvrmse_baseline',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='meterrun',
            name='cvrmse_reporting',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
