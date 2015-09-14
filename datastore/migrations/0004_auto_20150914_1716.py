# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0003_auto_20150911_2115'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dailyusagebaseline',
            options={'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='dailyusagereporting',
            options={'ordering': ['date']},
        ),
        migrations.RenameField(
            model_name='meterrun',
            old_name='model_type',
            new_name='meter_type',
        ),
    ]
