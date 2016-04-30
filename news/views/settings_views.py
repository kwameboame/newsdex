# coding=utf-8
import logging
from operator import setitem

from news.models import Feed
from news.tasks import twitter_task
from newsproject import celery_app
from django.shortcuts import render, redirect

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


def stop_stream(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        if task_id:
            celery_app.control.revoke(task_id=task_id, terminate=True)
    return redirect('settings')


def new_tweet_stream(request):
    if request.method == "POST":
        keyword = request.POST.get('keyword')
        location = request.POST.get('location')
        if location:
            location = [float(coordinate) for coordinate in location.split(',')]
        twitter_task.delay(keyword=keyword, location=location)
        return redirect('settings')
    return redirect('settings')
