# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0016_auto_20160122_2331'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectblock',
            old_name='project',
            new_name='projects',
        ),
        migrations.AddField(
            model_name='projectattribute',
            name='boolean_value',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='projectattribute',
            name='datetime_value',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='projectattribute',
            name='integer_value',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='projectattributekey',
            name='data_type',
            field=models.CharField(choices=[('BOOLEAN', 'boolean_value'), ('CHAR', 'char_value'), ('DATE', 'date_value'), ('DATETIME', 'datetime_value'), ('FLOAT', 'float_value'), ('INTEGER', 'integer_value')], max_length=25),
        ),
    ]
