# coding=utf-8
import logging

from django.shortcuts import render, redirect

from news.models import Feed
from news.tasks import twitter_task
from news.utils.common import get_active_tasks
from newsproject import celery_app

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def settings(request):
    feeds = Feed.objects.all()
    tasks_list = get_active_tasks(name='news.tasks.twitter_task.twitter_task')
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
