# coding=utf-8
import logging

from django.db import models

from news.models.nltk import Word

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


class TwitterUser(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Tweet(models.Model):
    tweet_id = models.CharField(max_length=255, unique=True)
    text = models.TextField()
    coordinates = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField()
    retweet_count = models.IntegerField()
    user = models.ForeignKey(TwitterUser)
    words = models.ManyToManyField(Word)

    def __str__(self):
        return "%s..." % self.text[:40]


class TwitterAPISetting(models.Model):
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.consumer_key
