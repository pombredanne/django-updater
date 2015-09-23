# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('updater', '0002_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registered', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='notification',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
