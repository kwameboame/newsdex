from celery.decorators import task
import requests
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
                article = Article.objects.get(url=entry.link)
                print('-- Article exist: --')
            except:
                article = Article() # we just create empty object
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
                    article.content = req.text
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

            print(article.title)

    print('== Done ==')