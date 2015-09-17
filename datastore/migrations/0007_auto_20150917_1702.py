# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0006_auto_20150915_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectblock',
            name='project_owner',
            field=models.ForeignKey(to='datastore.ProjectOwner', default=14),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='fuel_type',
            field=models.CharField(choices=[('NG', 'natural_gas'), ('E', 'electricity')], max_length=3),
        ),
    ]
