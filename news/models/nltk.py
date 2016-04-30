# coding=utf-8
import datetime
import logging

from django.db import models
from django.db.models import Count, Case, When, F

from news.utils.nltkutils import get_nltk_stop_words

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


class TagQuerySet(models.QuerySet):
    def tracked(self):
        return self.filter(tracked=True).annotate(
                articles_count=Count('word__article', distinct=True),
                posts_count=Count('word__facebookpost', distinct=True),
                comments_count=Count('word__facebookcomment', distinct=True),
                tweets_count=Count('word__tweet', distinct=True),
        )

    def tracked_for_articles(self):
        return self.tracked().filter(articles_count__gt=0)

    def tracked_for_posts(self):
        return self.tracked().filter(posts_count__gt=0)

    def tracked_for_comments(self):
        return self.tracked().filter(comments_count__gt=0)

    def tracked_for_tweets(self):
        return self.tracked().filter(tweets_count__gt=0)

    def get_top(self, field, date_from, date_to, count):
        """
        Returns top trending words (ignore case search) for given range of dates
        :param count: offset
        :type count: int
        :param date_to:
        :type date_to:
        :param date_from:
        :type date_from:
        :param field: one of the following: article | facebookpost | facebookcomment
        :type field: str
        """
        date_from_lookup = "word__%s__created_time__date__gte" % field
        date_to_lookup = "word__%s__created_time__date__lte" % field
        count_lookup = "%s_count" % field
        return self \
                   .non_stop_words() \
                   .filter(**{date_from_lookup: date_from, date_to_lookup: date_to}) \
                   .annotate(**{count_lookup: Count(Case(When(**{date_from_lookup: date_from, date_to_lookup: date_to, 'then': F('word__%s' % field)})), distinct=True)}) \
                   .order_by("-%s" % count_lookup)[:count]

    def _get_stop_words(self):
        from_db = set(self.filter(filtered=True).values_list('iword', flat=True))
        from_nltk = get_nltk_stop_words()
        return from_db.union(from_nltk)

    def non_stop_words(self):
        stop_words = self._get_stop_words()
        return self.exclude(iword__in=stop_words)


class Tag(models.Model):
    iword = models.CharField(max_length=200, unique=True)
    tracked = models.BooleanField(default=False)
    filtered = models.BooleanField(default=False)
    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.iword

    class Meta:
        ordering = ['-tracked', 'iword']


class Word(models.Model):
    word = models.CharField(max_length=200)
    pos = models.CharField(max_length=20, blank=True, null=True)
    created_time = models.DateTimeField(default=datetime.datetime.now)
    tag = models.ForeignKey(Tag)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['word']
        unique_together = ("word", "pos")
