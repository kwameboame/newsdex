# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-03 12:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0029_auto_20160430_1949'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilterKeyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='FilterLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('west_limit', models.FloatField()),
                ('east_limit', models.FloatField()),
                ('north_limit', models.FloatField()),
                ('south_limit', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='tweet',
            name='filter_keyword',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.FilterKeyword'),
        ),
        migrations.AddField(
            model_name='tweet',
            name='filter_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.FilterLocation'),
        ),
    ]
