# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-03 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0018_auto_20160403_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebookcomment',
            name='comment_id',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='facebookpost',
            name='post_id',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='facebookuser',
            name='user_id',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
