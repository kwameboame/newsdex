# coding=utf-8
import json
import logging
import time
from datetime import datetime, timedelta
from django.utils import timezone
from tweepy import StreamListener, OAuthHandler, Stream, API

from news.models import TwitterUser, Tweet, TwitterAPISetting
from news.models.twitter import FilterKeyword, FilterLocation, TwitterStream
from news.utils.common import chunks

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def authenticate(api_settings=None):
    if not api_settings:
        try:
            api_settings = TwitterAPISetting.objects.get()
        except TwitterAPISetting.MultipleObjectsReturned:
            logger.error('You have more than one twitter API settings! Go to admin page, and fix the problem.')
            raise Exception()
        except TwitterAPISetting.DoesNotExist:
            logger.error('You haven\'t got any twitter API settings! Go to admin page, and add one.')
            raise Exception()
    auth = OAuthHandler(api_settings.consumer_key, api_settings.consumer_secret)
    auth.set_access_token(api_settings.access_token, api_settings.access_token_secret)
    return auth


class SaveListener(StreamListener):
    def __init__(self, stream, api=None):
        self.stream = stream
        super().__init__(api)

    def save_tweet(self, tweet):
        dt_format = '%a %b %d %X %z %Y'
        data = {
            'text': tweet['text'],
            'created_time': datetime.strptime(tweet['created_at'], dt_format).strftime('%Y-%m-%d %H:%M:%S'),
            'tweet_id': tweet['id_str'],
            'coordinates': tweet.get('coordinates', None),
            'retweet_count': tweet.get('retweet_count', None),
            'user': TwitterUser.objects.get(user_id=tweet['user']['id_str']),
            'stream': self.stream,
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

    @staticmethod
    def is_retweet(tweet):
        if 'retweeted_status' in tweet:
            logger.debug('Retweet found: %s' % tweet['text'])
            return True
        return False

    def process_retweet(self, retweet):
        logger.debug('Getting original tweet from retweet')
        original_tweet = retweet['retweeted_status']
        self.save_twitter_user(original_tweet['user'])
        self.save_tweet(original_tweet)

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            logger.debug('%s %s:%s' % (tweet['created_at'], tweet['user']['name'], tweet['text']))
            if not self.is_retweet(tweet):
                self.save_twitter_user(tweet['user'])
                self.save_tweet(tweet)
            else:
                self.process_retweet(tweet)
            return True
        except Exception as e:
            logger.error(e)
            time.sleep(2)

    def on_error(self, status):
        logger.error('Error: status code %s' % status)


def subscribe_on_stream(task_id, api_settings=None, keyword=None, location=None):
    logger.debug('Starting parse twitter stream on keyword/location: "%s"' % (keyword or location))
    assert not (keyword and location), logger.error('Error: can\'t fetch by keyword and location in the same time!')
    assert keyword or location, logger.error('Nor keyword or location param is given')
    auth = authenticate(api_settings)
    if keyword:
        filter_keyword, created = FilterKeyword.objects.get_or_create(keyword=keyword)
        stream_obj = TwitterStream.objects.create(filter_keyword=filter_keyword, celery_task_id=task_id)
        l = SaveListener(stream=stream_obj)
        stream = Stream(auth, l)
        stream.filter(track=[keyword])
    if location:
        filter_location, created = FilterLocation.objects.get_or_create(west_limit=location[0], south_limit=location[1], east_limit=location[2], north_limit=location[3])
        stream_obj = TwitterStream.objects.create(filter_location=filter_location, celery_task_id=task_id)
        l = SaveListener(stream=stream_obj)
        stream = Stream(auth, l)
        stream.filter(locations=location)


def count_retweets():
    auth = authenticate()
    api = API(auth)
    week_ago = timezone.now().replace() - timedelta(days=7)
    tweets_ids = Tweet.objects.filter(created_time__gt=week_ago).values_list('tweet_id', flat=True)
    logger.debug('Count retweets for %s tweets from %s' % (tweets_ids.count(), week_ago))
    try:
        for chunk in chunks(tweets_ids, 100):
            for tweet in api.statuses_lookup(chunk):
                try:
                    tweet_obj = Tweet.objects.get(tweet_id=tweet.id_str)
                    logger.debug('Tweet %s::before - %s retweets, after - %s retweets' % (tweet_obj.tweet_id, tweet_obj.retweet_count, tweet.retweet_count))
                    tweet_obj.retweet_count = tweet.retweet_count
                    tweet_obj.save()
                except Exception as e:
                    logger.error(e)
    except Exception as e:
        logger.error(e)
    logger.debug('Finish count retweets!')
