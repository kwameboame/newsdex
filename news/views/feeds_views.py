# coding=utf-8
import datetime
import logging

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect

from news.forms import FeedForm
from news.models import Article, Feed
from news.tasks import ParseAllTask

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


def articles_list(request):
    articles = Article.objects.all().order_by('-created_time')
    rows = [articles[x:x + 1] for x in range(0, len(articles), 1)]
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

    return render(request, 'news/home.html', {'rows': rows})


def ajax_articles(request):
    if request.method == "GET":
        try:
            date_from = datetime.datetime.strptime(request.GET['date_from'], "%Y-%m-%d")
        except:
            date_from = datetime.date.today() - datetime.timedelta(days=5)
        try:
            date_to = datetime.datetime.strptime(request.GET['date_to'], "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except:
            date_to = datetime.date.today().replace(hour=23, minute=59, second=59)
        articles = Article.objects.filter(created_time__range=[date_from, date_to]).order_by('-created_time')
        rows = [articles[x:x + 1] for x in range(0, len(articles), 1)]

    return render(request, 'news/articles_cycle.html', locals())  # {'rows' : rows})


def feeds_list(request):
    feeds = Feed.objects.all()
    return render(request, 'news/feeds_list.html', {'feeds': feeds})


def new_feed(request):
    if request.method == "POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            url = request.POST.get('url')
            existingFeed = Feed.objects.filter(url=url)
            if len(existingFeed) == 0:
                ParseAllTask().delay(feed_url=url)
            return redirect('feeds_list')
    else:
        form = FeedForm()
    return render(request, 'news/new_feed.html', {'form': form})


def parse_manual(request):
    ParseAllTask().delay()
    return redirect('articles_list')
