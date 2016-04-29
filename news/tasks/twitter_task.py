# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import json
import time
import logging
from datetime import datetime

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from celery.task import task
from celery.signals import task_revoked

from news.models import TwitterUser, Tweet
from news.utils.twitterutils import ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """

    @staticmethod
    def save_tweet(tweet):
        dt_format = '%a %b %d %X %z %Y'
        data = {
            'text': tweet['text'],
            'created_time': datetime.strptime(tweet['created_at'], dt_format).strftime('%Y-%m-%d %H:%M:%S'),
            'tweet_id': tweet['id_str'],
            'coordinates': tweet.get('coordinates', None),
            'retweet_count': tweet.get('retweet_count', None),
            'user': TwitterUser.objects.get(user_id=tweet['user']['id_str'])
        }
        Tweet.objects.get_or_create(tweet_id=data['tweet_id'], defaults=data)

    @staticmethod
    def save_twitter_user(user):
        data = {
            'user_id': user['id_str'],
            'name': user['name'],
            'location': user.get('location'),
            'description': user.get('description'),
        }
        TwitterUser.objects.get_or_create(user_id=data['user_id'], defaults=data)

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            logger.warn(tweet['text'])
            logger.warn(tweet['created_at'])
            self.save_twitter_user(tweet['user'])
            self.save_tweet(tweet)
            return True
        except Exception as e:
            logger.error(e)
            time.sleep(2)

    def on_error(self, status):
        print(status)


@task
def twitter_task(keyword=None, location=None):
    logger.debug('Starting parse twitter stream on keyword/location: "%s"' % (keyword or location))
    l = StdOutListener()
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    stream = Stream(auth, l)
    if keyword:
        stream.filter(track=[keyword])
    if location:
        stream.filter(locations=location)
    logger.warn('Nor keyword or location param is given')


@task_revoked.connect(sender='news.streams.twitter_task.twitter_task')
def on_task_revoked():
    logger.warn('Twitter task revoked!')
