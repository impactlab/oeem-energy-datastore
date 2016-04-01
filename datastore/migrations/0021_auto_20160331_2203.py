# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0020_auto_20160219_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectattributekey',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
