# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import logging

from celery.signals import task_revoked
from celery.task import task
from django.utils.timezone import now

from news.models import TwitterStream

from news.utils.twitter_utils import subscribe_on_stream

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


@task(bind=True)
def twitter_task(self, keyword=None, location=None):
    subscribe_on_stream(keyword=keyword, location=location, task_id=self.request.id)


@task_revoked.connect
def on_task_revoked(request, terminated, signum, expired, *args, **kwargs):
    if request.task_name == 'news.tasks.twitter_task.twitter_task':
        stream = TwitterStream.objects.get(celery_task_id=request.id)
        stream.stopped = now()
        stream.save()
        logger.warn('Twitter task(%s) revoked!' % request.id)
