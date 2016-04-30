# coding=utf-8
import logging
from operator import setitem

from news.models import Feed
from newsproject import celery_app
from django.shortcuts import render

from tweepy.streaming import json

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def settings(request):
    feeds = Feed.objects.all()

    i = celery_app.control.inspect()
    active_tasks = i.active()
    tasks_list = []
    if isinstance(active_tasks, dict):
        try:
            tasks_list = active_tasks.popitem()[1]
            tasks_list = [task for task in tasks_list if task['name'] == 'news.tasks.twitter_task.twitter_task']
            [setitem(task, 'kwargs', json.loads(task['kwargs'].replace("'", '"'))) for task in tasks_list]
        except IndexError:
            pass
    return render(request, 'settings/settings.html', {'streams': tasks_list, 'feeds': feeds})
