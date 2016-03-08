# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0017_auto_20160125_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectattributekey',
            name='display_name',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
    ]
