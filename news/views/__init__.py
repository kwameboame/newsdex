# coding=utf-8
import logging

from .facebook_views import FacebookPostView
from .feeds_views import ajax_articles, articles_list, feeds_list, new_feed, parse_manual
from .nltk_views import ajax_nltk, get_by_word_and_date, nltk_list, nltk_all, TrackedWordView

__author__ = 'ilov3'
logger = logging.getLogger(__name__)
