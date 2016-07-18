# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-13 00:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0028_auto_20160713_0000'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datastore.Project')),
            ],
        ),
    ]