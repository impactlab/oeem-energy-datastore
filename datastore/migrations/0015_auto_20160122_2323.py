# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0014_auto_20151026_2137'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('char_value', models.CharField(max_length=100, blank=True, null=True)),
                ('float_value', models.FloatField(blank=True, null=True)),
                ('date_value', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectAttributeKey',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('data_type', models.CharField(choices=[('FLOAT', 'float_value'), ('CHAR', 'char_value'), ('DATE', 'date_value')], max_length=25)),
            ],
        ),
        migrations.AlterField(
            model_name='consumptionmetadata',
            name='fuel_type',
            field=models.CharField(choices=[('NG', 'natural_gas'), ('E', 'electricity')], max_length=3),
        ),
        migrations.AlterField(
            model_name='fueltypesummary',
            name='fuel_type',
            field=models.CharField(choices=[('NG', 'natural_gas'), ('E', 'electricity')], max_length=3),
        ),
        migrations.AddField(
            model_name='projectattribute',
            name='key',
            field=models.ForeignKey(to='datastore.ProjectAttributeKey'),
        ),
        migrations.AddField(
            model_name='projectattribute',
            name='project',
            field=models.ForeignKey(to='datastore.Project'),
        ),
    ]
