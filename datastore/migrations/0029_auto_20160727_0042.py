# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-27 00:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0028_auto_20160721_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectresult',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_results', to='datastore.Project'),
        ),
    ]