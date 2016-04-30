# coding=utf-8
import logging

from django.shortcuts import render

from news.models import Tweet

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def tweets_list(request):
    tweets = Tweet.objects.all()
    return render(request, 'twitter/tweets_list.html', {'tweets': tweets})
