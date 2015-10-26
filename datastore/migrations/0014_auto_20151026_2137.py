# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0013_auto_20151008_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='energy_unit',
            field=models.CharField(choices=[('THM', 'therm'), ('KWH', 'kWh')], max_length=3),
        ),
    ]
