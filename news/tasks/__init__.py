# coding=utf-8
import logging
from .parse_tasks import ParseAllTask, ParseFeedTask, ParseFacebookTask
from .nltk_tasks import nltk_all_task
from .twitter_task import twitter_task

__author__ = 'ilov3'
logger = logging.getLogger(__name__)
