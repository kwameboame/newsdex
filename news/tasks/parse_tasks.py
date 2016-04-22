# coding=utf-8
import datetime
import logging
import re
from urllib.error import HTTPError

import facebook
import feedparser
import requests
from celery import Task
from django.db.models import Q
from readability import Document

from news.models import Feed, Article, FacebookPost, FacebookComment, FacebookUser, FacebookPage
from news.tasks.utils import get_access_token, FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def parse_feed(feed_urls):
    logger.debug('== Let try to parse all of feeds ==')
    logger.debug('There are count feeds:')
    logger.debug(len(feed_urls))
    for url in feed_urls:
        feedData = feedparser.parse(url)
        feedTitle = feedData.feed.title
        try:
            feed = Feed.objects.get(url=url)
        except Feed.DoesNotExist:
            feed = Feed.objects.create(url=url, title=feedTitle)
        except Feed.MultipleObjectsReturned:
            feed = Feed.objects.filter(url=url).last()
            logger.warn('Feed "%s" has duplicates!' % feedTitle)
        logger.debug('== Feed is: ==')
        logger.debug(feed.title)
        logger.debug('-- There are entries in feed: --') 
        logger.debug(len(feedData.entries))
        for entry in feedData.entries:
            try:
                article = Article.objects.get(Q(url=entry.link) | Q(title=entry.title))
                logger.info('-- Article exist: --')
            except Article.MultipleObjectsReturned:
                logger.warn('You have duplicate articles. Duplicate: "%s"' % entry.title)
            except Article.DoesNotExist:
                article = Article()  # we just create empty object
                article.title = entry.title
                article.url = entry.link
                article.description = entry.description
                try:
                    req = requests.get(entry.link,
                                       headers={
                                           'Accept': 'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1',
                                           'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.9.5) Presto/2.12.388 Version/12.15',
                                           'Accept-Encoding': 'gzip, deflate',
                                           'Connection': 'close'
                                       })
                    article.content = re.sub('<[^<]+?>', '', Document(req.text).summary())
                    d = datetime.datetime(*(entry.published_parsed[0:6]))
                    dateString = d.strftime('%Y-%m-%d %H:%M:%S')

                    article.created_time = dateString
                    article.feed = feed
                    article.save()

                    print('-- Added article: --')

                except HTTPError as inst:
                    output = format(inst)
                    logger.error('-- Error: --')
                    logger.error(output)
                    logger.error('-- Failed to add article: --')
                else:
                    logger.debug('-- Article exist: --')
            try:
                logger.debug(article.title)
            except Exception as e:
                logger.error(e)


def parse_facebook(pages):
    access_token = get_access_token(FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET)
    if access_token is not None:
        logger.debug('== Let try to parse all of facebook links ==')
        for page in pages:
            logger.debug('== Parse page: ==')
            try:
                logger.debug(page.title)
            except Exception as e:
                logger.debug('Unavaliable to print page.title data. %s' % e)
            try:
                graph = facebook.GraphAPI(access_token=access_token, version='2.5')
                profile = graph.get_object(page.url)
                try:
                    logger.debug(profile)
                except Exception as e:
                    print('Unavaliable to print profile data. %s' % e)
                posts = graph.get_connections(profile['id'], 'posts')
                logger.debug('-- Get data: --')
                # try:
                #     print(posts)
                # except:
                #     print('Unavaliable to print posts data')
                for post in posts['data']:
                    logger.debug('-- Here is post: --')
                    try:
                        logger.debug(post)
                    except Exception as e:
                        print('Unavaliable to print post data. %s' % e)
                    try:
                        new_post = FacebookPost.objects.get(post_id=post['id'])
                        logger.debug('-- Post exist in db --')
                    except FacebookPost.MultipleObjectsReturned:
                        logger.warn('You have duplicate posts. Duplicate: "%s"' % post['id'])
                    except FacebookPost.DoesNotExist:
                        new_post = FacebookPost()
                        new_post.parent_page = page
                        logger.debug(post['created_time'])
                        new_post.created_time = datetime.datetime.strptime((post['created_time']).split("+")[0], '%Y-%m-%dT%H:%M:%S')
                        if 'message' in post:
                            new_post.text = post['message']
                        elif 'story' in post:
                            new_post.text = post['story']
                        new_post.post_id = post['id']
                        new_post.save()
                        logger.debug('-- Post saved in db --')

                    logger.info('## Comments data ##')
                    comments = graph.get_connections(id=post['id'], connection_name='comments')
                    for comment in comments['data']:
                        logger.debug('-- Here is comment: --')
                        try:
                            logger.debug(comment)
                        except Exception as e:
                            logger.debug('Unavaliable to print comment data. %s' % e)
                        try:
                            new_comment = FacebookComment.objects.get(comment_id=comment['id'])
                            logger.debug('-- Comment exist in db --')
                        except FacebookComment.MultipleObjectsReturned:
                            logger.debug('You have duplicate comments. Duplicate: "%s"' % comment['id'])
                        except FacebookComment.DoesNotExist:
                            try:
                                new_user = FacebookUser.objects.get(user_id=comment['from']['id'])
                                logger.debug('-- User exist in db --')
                            except FacebookUser.MultipleObjectsReturned:
                                logger.debug('You have duplicate fb users. Duplicate: "%s"' % comment['from']['name'])
                            except FacebookUser.DoesNotExist:
                                new_user = FacebookUser()
                                new_user.user_id = comment['from']['id']
                                new_user.name = comment['from']['name']
                                new_user.save()
                                logger.debug('-- New user added to db --')
                            new_comment = FacebookComment()
                            new_comment.post_id = new_post
                            new_comment.user_id = new_user
                            new_comment.created_time = datetime.datetime.strptime((comment['created_time']).split("+")[0], '%Y-%m-%dT%H:%M:%S')
                            if 'message' in comment:
                                new_comment.message = comment['message']
                            elif 'story' in comment:
                                new_comment.message = comment['story']
                            new_comment.comment_id = comment['id']
                            new_comment.save()
                            logger.debug('-- Comment saved in db --')
            except Exception as e:
                print('Error parsing fb. %s' % e)
    else:
        logger.warn('-- Access token is None --')


class ParseFeedTask(Task):
    def run(self, feed_url=None):
        if feed_url:
            parse_feed([feed_url])
        else:
            feed_urls = [item[0] for item in Feed.objects.filter(is_active=True).values_list('url')]
            parse_feed(feed_urls)


class ParseFacebookTask(Task):
    def run(self, page=None):
        if page:
            parse_facebook([page])
        else:
            pages = FacebookPage.objects.filter(is_active=True)
            parse_facebook(pages)


class ParseAllTask(Task):
    def run(self, feed_url=None, page=None, *args):
        ParseFacebookTask()(page=page)
        ParseFeedTask()(feed_url=feed_url)
        logger.debug('== Done ==')