# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0012_auto_20151006_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyusagesummaryactual',
            name='n_projects',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='monthlyusagesummaryactual',
            name='n_projects',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
