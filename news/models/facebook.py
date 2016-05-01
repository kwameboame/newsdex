# coding=utf-8
import logging

import requests
from django.db import models

from news.models.nltk import Word

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


class FacebookPage(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class FacebookPost(models.Model):
    parent_page = models.ForeignKey(FacebookPage)
    created_time = models.DateTimeField()
    text = models.TextField()
    post_id = models.CharField(max_length=255, unique=True)
    words = models.ManyToManyField(Word)
    nltkized = models.BooleanField(default=False)

    def __str__(self):
        return "%s..." % self.text[:40]


class FacebookUser(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class FacebookComment(models.Model):
    post_id = models.ForeignKey(FacebookPost, blank=True, null=True)
    user_id = models.ForeignKey(FacebookUser)
    created_time = models.DateTimeField()
    message = models.TextField()
    comment_id = models.CharField(max_length=255, unique=True)
    words = models.ManyToManyField(Word)
    nltkized = models.BooleanField(default=False)

    def __str__(self):
        return "%s..." % self.message[:40]


class FacebookAPISetting(models.Model):
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.client_id

    def get_access_token(self):
        url = 'https://graph.facebook.com/oauth/access_token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }
        req = requests.get(url, params=params)
        s = req.text.split('=')
        if (s[0] == 'access_token') and (len(s) == 2):
            return s[1]
        else:
            return None
