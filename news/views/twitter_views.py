# coding=utf-8
import logging

import datetime
from django.shortcuts import render

from news.models import Tweet, TwitterStream

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def tweets_list(request, task_id=None):
    context = {}
    if task_id:
        stream = TwitterStream.objects.get(celery_task_id=task_id)
        context['stream'] = stream
        context['tweets'] = stream.tweet_set.all()
    else:
        context['tweets'] = Tweet.objects.all()
    return render(request, 'twitter/tweets_list.html', context)


def streams_list(request):
    return render(request, 'twitter/streams_list.html')


def streams_cycle(request):
    try:
        date_from = datetime.datetime.strptime(request.GET['date_from'], "%Y-%m-%d")
    except:
        date_from = datetime.datetime.today() - datetime.timedelta(days=5)
    try:
        date_to = datetime.datetime.strptime(request.GET['date_to'], "%Y-%m-%d")
    except:
        date_to = datetime.datetime.today()
    date_to = date_to.replace(hour=23, minute=59, second=59)
    streams = TwitterStream.objects.filter(started__lte=date_to, stopped__gte=date_from).count_tweets()
    return render(request, 'twitter/streams_cycle.html', {'streams': streams})
