# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datastore', '0018_projectattributekey_display_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectblock',
            name='project_owner',
        ),
    ]
