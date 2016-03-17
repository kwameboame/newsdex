from celery.decorators import task
import http.cookiejar, urllib.request
import feedparser
from news import views
from .models import *
import datetime 



@task
def parse(*args):
    feeds = Feed.objects.filter(is_active=True)
    print('== Let try to parse all of feeds ==')
    print(feeds)
    for feed in feeds:
        feedData = feedparser.parse(feed.url)
        print('-- Feed is: --')
        print(feed.title)
        print('-- There are entries in feed: --')
        print(len(feedData.entries))
        for entry in feedData.entries:
            try:
                article = Article.objects.get(url=entry.link).order_by('-publication_date')
                print('-- Article exist: --')
            except:
                article = Article().order_by('-publication_date')
                article.title = entry.title
                article.url = entry.link
                article.description = entry.description
                # cj = http.cookiejar.CookieJar()
                # opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
                # url_open = opener.open(article.url)
                # article.content = url_open.read()
                # article.content = urlopen(article.url).read()

                d = datetime.datetime(*(entry.published_parsed[0:6]))
                dateString = d.strftime('%Y-%m-%d %H:%M:%S')

                article.publication_date = dateString
                article.feed = feed
                article.save()

                print('-- Added article: --')

            print(article.title)

    print('== Done ==')