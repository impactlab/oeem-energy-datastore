# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meterrun',
            old_name='model_parameter_json',
            new_name='model_parameter_json_baseline',
        ),
        migrations.AddField(
            model_name='meterrun',
            name='model_parameter_json_reporting',
            field=models.CharField(max_length=10000, null=True, blank=True),
        ),
    ]
