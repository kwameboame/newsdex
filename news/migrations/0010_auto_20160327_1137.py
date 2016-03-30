# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-27 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0009_auto_20160327_1000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tracked_word',
            name='facebook_comment',
        ),
        migrations.RemoveField(
            model_name='tracked_word',
            name='facebook_post',
        ),
        migrations.RemoveField(
            model_name='tracked_word',
            name='news_article',
        ),
        migrations.AddField(
            model_name='article',
            name='tracked_word',
            field=models.ManyToManyField(to='news.Tracked_Word'),
        ),
    ]