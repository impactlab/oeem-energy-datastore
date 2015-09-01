# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConsumptionMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fuel_type', models.CharField(max_length=3, choices=[(b'E', b'electricity'), (b'NG', b'natural_gas')])),
                ('fuel_unit', models.CharField(max_length=3, choices=[(b'KWH', b'kilowatthours'), (b'THM', b'therms')])),
            ],
        ),
        migrations.CreateModel(
            name='ConsumptionRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('value', models.FloatField(null=True, blank=True)),
                ('estimated', models.BooleanField()),
                ('metadata', models.ForeignKey(related_name='records', to='datastore.ConsumptionMetadata')),
            ],
            options={
                'ordering': ['start'],
            },
        ),
    ]
