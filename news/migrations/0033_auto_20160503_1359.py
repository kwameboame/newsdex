# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-03 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0032_auto_20160503_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twitterstream',
            name='stopped',
            field=models.DateTimeField(null=True),
        ),
    ]
