# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-22 09:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_facebookcomment_post_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='words',
            field=models.ManyToManyField(to='news.Word'),
        ),
    ]
