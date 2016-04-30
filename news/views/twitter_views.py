# coding=utf-8
import logging

from newsproject import celery_app
from django.shortcuts import redirect, render

from news.models import Tweet
from news.tasks import twitter_task

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def tweets_list(request):
    tweets = Tweet.objects.all()
    return render(request, 'twitter/tweets_list.html', {'tweets': tweets})


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
