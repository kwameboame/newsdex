from celery.decorators import task
import requests
import feedparser
from .models import *
import datetime
from readability.readability import Document
import re
import facebook


FACEBOOK_CLIENT_ID = '105323143198945'
FACEBOOK_CLIENT_SECRET = 'e10beb3dc3a388480927d29493168545'


def get_access_token(client_id, client_secret):
    url = 'https://graph.facebook.com/oauth/access_token'
    params = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'client_credentials',

    }
    req = requests.get(url, params=params)
    s = req.text.split('=')
    if (s[0] == 'access_token') and (len(s) == 2):
        return s[1]
    else:
        return None


def parse_feed(feeds):
    print('== Let try to parse all of feeds ==')
    print('There are count feeds:')
    print(len(feeds))
    for feed in feeds:
        feedData = feedparser.parse(feed.url)
        print('== Feed is: ==')
        print(feed.title)
        print('-- There are entries in feed: --')
        print(len(feedData.entries))
        for entry in feedData.entries:
            try:
                article = Article.objects.get(url=entry.link)
                print('-- Article exist: --')
            except:
                article = Article.objects.filter(title=entry.title)
                if len(article) == 0:
                    article = Article()  # we just create empty object
                    article.title = entry.title
                    article.url = entry.link
                    article.description = entry.description
                    try:
                        req=requests.get(entry.link,
                            headers= { 
                                'Accept': 'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1', 
                                'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.9.5) Presto/2.12.388 Version/12.15', 
                                'Accept-Encoding': 'gzip, deflate', 
                                'Connection': 'close'
                                }
                            )                
                        article.content = re.sub('<[^<]+?>', '', Document(req.text).summary())
                        d = datetime.datetime(*(entry.published_parsed[0:6]))
                        dateString = d.strftime('%Y-%m-%d %H:%M:%S')

                        article.publication_date = dateString
                        article.feed = feed
                        article.save()

                        print('-- Added article: --')

                    except urllib.request.HTTPError as inst:
                        output = format(inst)
                        print('-- Error: --')
                        print(output)
                        print('-- Failed to add article: --')
                else:
                    print('-- Article exist: --')
            try:
                print(article.title)
            except:
                print(':( Unable to output article title')


def parse_facebook(pages):
    access_token = get_access_token(FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET)
    if access_token is not None:
        print('== Let try to parse all of facebook links ==')
        for page in pages:
            print('== Parse page: ==')
            try:
                print(page.title)
            except:
                print('Unavaliable to print page.title data')
            try:
                graph = facebook.GraphAPI(access_token=access_token, version='2.5')
                profile = graph.get_object(page.url)
                try:
                    print(profile)
                except:
                    print('Unavaliable to print profile data')
                posts = graph.get_connections(profile['id'], 'posts')
                print('-- Get data: --')
                # try:
                #     print(posts)
                # except:
                #     print('Unavaliable to print posts data')
                for post in posts['data']:
                    print('-- Here is post: --')
                    try:
                        print(post)
                    except:
                        print('Unavaliable to print post data')
                    try:
                        new_post = FacebookPost.objects.get(post_id=post['id'])
                        print('-- Post exist in db --')
                    except:
                        new_post = FacebookPost()
                        new_post.parent_page = page
                        print(post['created_time'])
                        new_post.created_time = datetime.datetime.strptime((post['created_time']).split("+")[0], '%Y-%m-%dT%H:%M:%S')
                        if 'message' in post:
                            new_post.text = post['message']
                        elif 'story' in post:
                            new_post.text = post['story']
                        new_post.post_id = post['id']
                        new_post.save()
                        print('-- Post saved in db --')
                        
                    print('## Comments data ##')
                    comments = graph.get_connections(id=post['id'], connection_name='comments')
                    for comment in comments['data']:
                        print('-- Here is comment: --')
                        try:
                            print(comment)
                        except:
                            print('Unavaliable to print comment data')
                        try:
                            new_comment = FacebookComment.objects.get(comment_id=comment['id'])
                            print('-- Comment exist in db --')
                        except:
                            try:
                                new_user = FacebookUser.objects.get(user_id=comment['from']['id'])
                                print('-- User exist in db --')
                            except:
                                new_user = FacebookUser()
                                new_user.user_id = comment['from']['id']
                                new_user.name = comment['from']['name']
                                new_user.save()
                                print('-- New user added to db --')
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
                            print('-- Comment saved in db --')
            except:
                print('-- Something went wrong :( --')
    else:
        print('-- Access token is None --')
        pass

@task
def parse(feed=None, page=None, *args):
    if feed:
        parse_feed([feed])
    else:
        feeds = Feed.objects.filter(is_active=True)
        parse_feed(feeds)
    if page:
        parse_facebook([page])
    else:
        pages = FacebookPage.objects.filter(is_active=True)
        parse_facebook(pages)

    print('== Done ==')
