# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0005_auto_20150902_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='energy_unit',
            field=models.CharField(max_length=3, choices=[(b'KWH', b'kWh'), (b'THM', b'therm')]),
        ),
        migrations.AlterField(
            model_name='meterrun',
            name='serialization',
            field=models.CharField(max_length=100000, null=True, blank=True),
        ),
    ]
