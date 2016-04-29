# coding=utf-8
import logging
from operator import setitem

from celery.task.control import inspect
from django.shortcuts import render

from tweepy.streaming import json

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def streams(request):
    i = inspect()
    active_tasks = i.active()
    tasks_list = []
    if isinstance(active_tasks, dict):
        try:
            tasks_list = active_tasks.popitem()[1]
            tasks_list = [task for task in tasks_list if task['name'] == 'news.tasks.twitter_task.twitter_task']
            [setitem(task, 'kwargs', json.loads(task['kwargs'].replace("'", '"'))) for task in tasks_list]
        except IndexError:
            pass
    return render(request, 'misc/streams.html', {'streams': tasks_list})
