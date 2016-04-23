# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-25 22:59
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0023_auto_20160525_2043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meterrun',
            name='meter_type',
        ),
        migrations.RemoveField(
            model_name='projectrun',
            name='meter_type',
        ),
        migrations.AddField(
            model_name='meterrun',
            name='meter_class',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='meterrun',
            name='meter_settings',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='projectrun',
            name='meter_class',
            field=models.CharField(default=b'DefaultResidentialMeter', max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='projectrun',
            name='meter_settings',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]