# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-03 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0034_twitterstream_celery_task_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twitterstream',
            name='celery_task_id',
            field=models.CharField(max_length=255),
        ),
    ]
