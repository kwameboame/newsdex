from celery.decorators import task
import feedparser
from news import views
from .models import *
import datetime 

@task
def parse(*args):
    feeds = Feed.objects.filter(is_active=True)
    print('Let try to parse all of feeds')
    for feed in feeds:
        feedData = feedparser.parse(feed.url)

        for entry in feedData.entries:
            try:
                article = Article.objects.get(url=entry.link)
                print('Article exist:')
            except:
                article = Article()
                article.title = entry.title
                article.url = entry.link
                article.description = entry.description

                d = datetime.datetime(*(entry.published_parsed[0:6]))
                dateString = d.strftime('%Y-%m-%d %H:%M:%S')

                article.publication_date = dateString
                article.feed = feed
                article.save()

                print('Added article:')

            print(article.title)

    print('Done')