# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-03 13:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0030_auto_20160503_1235'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterStream',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started', models.DateTimeField(auto_now=True)),
                ('stopped', models.DateTimeField()),
                ('filter_keyword', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.FilterKeyword')),
                ('filter_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.FilterLocation')),
            ],
        ),
        migrations.RemoveField(
            model_name='tweet',
            name='filter_keyword',
        ),
        migrations.RemoveField(
            model_name='tweet',
            name='filter_location',
        ),
        migrations.AddField(
            model_name='tweet',
            name='stream',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.TwitterStream'),
        ),
    ]
