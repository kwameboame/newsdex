from celery.decorators import task
import feedparser
from news import views
from .models import *
import datetime 

@task
def parse(*args):
    url = 'http://www.myjoyonline.com/pages/rss/site_politics.xml'
    feedData = feedparser.parse(url)

    try:
        feed = Feed.objects.get(url=url)
    except:
        feed = Feed(url=url)
        feed.title = feedData.feed.title
        feed.save()

    for entry in feedData.entries:
        article = Article()
        article.title = entry.title
        article.url = entry.link
        article.description = entry.description

        d = datetime.datetime(*(entry.published_parsed[0:6]))
        dateString = d.strftime('%Y-%m-%d %H:%M:%S')

        article.publication_date = dateString
        article.feed = feed
        article.save()

    print(feedData.entries)
    print('done')
