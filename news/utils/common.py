# coding=utf-8
import logging
from operator import setitem

from tweepy.streaming import json
from newsproject import celery_app

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def get_active_tasks(name=None):
    tasks_list = []
    try:
        i = celery_app.control.inspect()
        active_tasks = i.active()
        if isinstance(active_tasks, dict):
            tasks_list = [item for sub_list in active_tasks.values() for item in sub_list]
            tasks_list = [task for task in tasks_list if (task['name'] == name or not name)]
            [setitem(task, 'kwargs', json.loads(task['kwargs'].replace("'", '"'))) for task in tasks_list]
    except Exception as e:
        logger.error('Error: %s' % e)
    return tasks_list


chunks = lambda l, n: [l[i:i + n] for i in range(0, len(l), n)]
