# coding=utf-8
import logging

from django.db import models

from news.models.nltk import Word

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


class Feed(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Article(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=200, unique=True)
    url = models.URLField(unique=True)
    description = models.TextField()
    content = models.TextField(default="")
    created_time = models.DateTimeField()
    words = models.ManyToManyField(Word)
    nltkized = models.BooleanField(default=False)

    def __str__(self):
        return self.title
