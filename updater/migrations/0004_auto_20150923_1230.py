# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('updater', '0003_auto_20150923_0854'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Token',
        ),
        migrations.AddField(
            model_name='status',
            name='site_token',
            field=models.CharField(default=uuid.uuid4, max_length=36),
        ),
    ]
