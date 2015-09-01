# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('datastore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnualSavings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='AnnualUsageBaseline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='AnnualUsageReporting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DailyUsageBaseline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='DailyUsageReporting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='GrossSavings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='MeterRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serialization', models.CharField(max_length=100000)),
                ('consumption_metadata_id', models.ForeignKey(to='datastore.ConsumptionMetadata')),
            ],
        ),
        migrations.CreateModel(
            name='ModelParameters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parameters_json', models.CharField(max_length=255)),
                ('meter_run', models.ForeignKey(to='datastore.MeterRun')),
            ],
        ),
        migrations.CreateModel(
            name='ModelType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='project_owner',
            field=models.ForeignKey(to='datastore.ProjectOwner'),
        ),
        migrations.AddField(
            model_name='modelparameters',
            name='model_type',
            field=models.ForeignKey(to='datastore.ModelType'),
        ),
        migrations.AddField(
            model_name='meterrun',
            name='project',
            field=models.ForeignKey(to='datastore.Project'),
        ),
        migrations.AddField(
            model_name='grosssavings',
            name='meter_run',
            field=models.ForeignKey(to='datastore.MeterRun'),
        ),
        migrations.AddField(
            model_name='dailyusagereporting',
            name='meter_run',
            field=models.ForeignKey(to='datastore.MeterRun'),
        ),
        migrations.AddField(
            model_name='dailyusagebaseline',
            name='meter_run',
            field=models.ForeignKey(to='datastore.MeterRun'),
        ),
        migrations.AddField(
            model_name='block',
            name='project',
            field=models.ManyToManyField(to='datastore.Project'),
        ),
        migrations.AddField(
            model_name='annualusagereporting',
            name='meter_run',
            field=models.ForeignKey(to='datastore.MeterRun'),
        ),
        migrations.AddField(
            model_name='annualusagebaseline',
            name='meter_run',
            field=models.ForeignKey(to='datastore.MeterRun'),
        ),
        migrations.AddField(
            model_name='annualsavings',
            name='meter_run',
            field=models.ForeignKey(to='datastore.MeterRun'),
        ),
        migrations.AddField(
            model_name='consumptionmetadata',
            name='project',
            field=models.ForeignKey(blank=True, to='datastore.Project', null=True),
        ),
    ]
