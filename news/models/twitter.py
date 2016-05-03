# coding=utf-8
import logging

from django.db import models
from django.db.models import Count

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


class FilterKeyword(models.Model):
    keyword = models.CharField(max_length=255)

    def __str__(self):
        return self.keyword


class FilterLocation(models.Model):
    west_limit = models.FloatField()
    east_limit = models.FloatField()
    north_limit = models.FloatField()
    south_limit = models.FloatField()

    def __str__(self):
        return '%s' % self.get_location()

    def get_location(self):
        return [self.west_limit, self.south_limit, self.east_limit, self.north_limit]


class TwitterStreamQuerySet(models.QuerySet):
    def count_tweets(self):
        return self.annotate(tweets_count=Count('tweet'))


class TwitterStream(models.Model):
    started = models.DateTimeField(auto_now_add=True)
    stopped = models.DateTimeField(null=True)
    filter_keyword = models.ForeignKey(FilterKeyword, null=True, blank=True)
    filter_location = models.ForeignKey(FilterLocation, null=True, blank=True)
    celery_task_id = models.CharField(max_length=255)
    objects = TwitterStreamQuerySet.as_manager()

    def __str__(self):
        return "%s - %s::%s" % (self.started, self.stopped, (self.filter_keyword or self.filter_location))


class Tweet(models.Model):
    tweet_id = models.CharField(max_length=255, unique=True)
    text = models.TextField()
    coordinates = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField()
    retweet_count = models.IntegerField()
    user = models.ForeignKey(TwitterUser)
    words = models.ManyToManyField(Word)
    nltkized = models.BooleanField(default=False)
    stream = models.ForeignKey(TwitterStream)

    def __str__(self):
        return "%s..." % self.text[:40]


class TwitterAPISetting(models.Model):
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.consumer_key
