# coding=utf-8
import logging

from celery.task import task
from django.db import OperationalError

from news.models import Word, Article, FacebookPost, FacebookComment, Tag, Tweet
from news.utils.nltkutils import get_most_common_words

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
                    new_word = Word.objects.get(word=word, pos=pos)
                    logger.debug('Word exists in db')
                except Word.DoesNotExist:  # lets specify our exception
                    iword = word.lower()
                    new_tag, created = Tag.objects.get_or_create(iword=iword)
                    new_word = Word(word=word, pos=pos, tag=new_tag)
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
            obj.nltkized = True
            obj.save()

    articles = Article.objects.all().filter(nltkized=False)
    posts = FacebookPost.objects.all().filter(nltkized=False)
    comments = FacebookComment.objects.all().filter(nltkized=False)
    tweets = Tweet.objects.all().filter(nltkized=False)

    add_words(tweets, 'tweet_id', 'text')
    add_words(articles, 'title', 'content')
    add_words(posts, 'post_id', 'text')
    add_words(comments, 'comment_id', 'message')

    logger.debug('Finish!')
