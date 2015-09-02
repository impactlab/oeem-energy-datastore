# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0002_auto_20150901_2151'),
    ]

    operations = [
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField(null=True, blank=True)),
                ('end', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.RenameField(
            model_name='consumptionmetadata',
            old_name='fuel_unit',
            new_name='energy_unit',
        ),
        migrations.AddField(
            model_name='project',
            name='latitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='longitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='weather_station',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='zipcode',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='baseline_period',
            field=models.OneToOneField(related_name='baseline_period', null=True, blank=True, to='datastore.Period'),
        ),
        migrations.AddField(
            model_name='project',
            name='reporting_period',
            field=models.OneToOneField(related_name='reporting_period', null=True, blank=True, to='datastore.Period'),
        ),
    ]
