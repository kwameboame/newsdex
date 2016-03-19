from django.shortcuts import render, redirect
import requests
from readability.readability import Document
import re
from .models import *
from .forms import FeedForm
from .tasks import parse, parse_feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import feedparser
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import sys


def print_http_response(f):
    """ Wraps a python function that prints to the console, and
    returns those results as a HttpResponse (HTML)"""

    class WritableObject:
        def __init__(self):
            self.content = []

        def write(self, string):
            self.content.append(string)

    def new_f(*args, **kwargs):
        printed = WritableObject()
        sys.stdout = printed
        f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        return HttpResponse(['<BR>' if c == '\n' else c for c in printed.content ])
    return new_f
# Create your views here.


def articles_list(request):
    articles = Article.objects.all().order_by('-publication_date')
    rows = [articles[x:x+1] for x in range(0, len(articles), 1)]
    # return render(request, 'news/articles_list.html', {'rows': rows})

    paginator = Paginator(articles, 25)  # Show 25 articles per page

    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articles = paginator.page(paginator.num_pages)

    # context = {
    # 'object_list':rows,
    # 'title' : 'list'
    # }

    return render(request, 'news/articles_list.html', {'rows': rows})


@csrf_exempt
def ajax_articles(request):
    rows = []
    if request.method == "GET":
        try:
            date_from = datetime.datetime.strptime(request.GET['date_from'], "%Y-%m-%d")
        except:
            date_from = datetime.date.today() - datetime.timedelta(days=5)
        try:
            date_to = datetime.datetime.strptime(request.GET['date_to'], "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except:
            date_to = datetime.date.today().replace(hour=23, minute=59, second=59)
        articles = Article.objects.filter(publication_date__range=[date_from, date_to]).order_by('-publication_date')
        rows = [articles[x:x+1] for x in range(0, len(articles), 1)]

    return render(request, 'news/articles_cycle.html', locals())# {'rows' : rows})


###Feeds Listing
def feeds_list(request):
    feeds = Feed.objects.all()
    return render(request, 'news/feeds_list.html', {'feeds': feeds})


def new_feed(request):
    if request.method == "POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            feed = form.save(commit=False)

            existingFeed = Feed.objects.filter(url=feed.url)
            if len(existingFeed) == 0:
                feedData = feedparser.parse(feed.url)

                # set some fields
                feed.title = feedData.feed.title
                feed.save()
                parse_feed([feed])
            return redirect('news.views.feeds_list')
    else:
        form = FeedForm()
    return render(request, 'news/new_feed.html', {'form': form})


@print_http_response
def parse_manual(request):
    parse()
