# coding=utf-8
import logging

from celery.task import task
from django.db import OperationalError
from django.db.models import Q

from news.models import Word, Article, FacebookPost, FacebookComment
from .utils import get_most_common_words

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


@task
def nltk_all_task():
    def add_words(queryset, lookup_title, lookup_content):
        for obj in queryset:
            logger.debug('Get %s:' % obj._meta.model_name)
            logger.debug(getattr(obj, lookup_title))
            words = get_most_common_words(getattr(obj, lookup_content), 10, remove_stopwords=True)
            logger.debug('Words are:')
            for word in words:
                word, pos = word['word']
                logger.debug(word)
                try:
                    new_word = Word.objects.get(Q(word__iregex='^%s$' % word), Q(pos=pos) | Q(tracked=True))  # => word='^word$' AND (pos=pos OR tracked=True)
                    if new_word.tracked and not obj.words.filter(word=new_word).exists():
                        obj.words.add(new_word)
                        obj.save()
                        logger.debug('Tracked word "%s" added to %s' % (word, obj._meta.model_name))
                    logger.debug('Word exists in db')
                except Word.DoesNotExist:  # lets specify our exception
                    new_word = Word(word=word, pos=pos)
                    new_word.save()
                    logger.debug('Thats new word!')
                except Word.MultipleObjectsReturned:
                    logger.warn('Word "%s" has duplicates!' % word)
                except OperationalError:
                    logger.error('Can\'t fetch the word "%s".' % word)
                try:
                    if not obj.words.filter(word=new_word).exists():
                        obj.words.add(new_word)
                        obj.save()
                        logger.debug('Word added to %s' % obj._meta.model_name)
                    else:
                        logger.debug('Word exists in %s' % obj._meta.model_name)
                except Exception as e:  # and even if we don't know what it actually was catch it and print or log it
                    logger.error('Something went wrong! The error was: %s' % e)

    articles = Article.objects.all()
    posts = FacebookPost.objects.all()
    comments = FacebookComment.objects.all()

    add_words(articles, 'title', 'content')
    add_words(posts, 'post_id', 'text')
    add_words(comments, 'comment_id', 'message')
