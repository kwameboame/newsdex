from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.articles_list, name='articles_list'),
    url(r'^ajax_articles', views.ajax_articles, name='ajax_articles'),

    url(r'^feeds/new', views.new_feed, name='feed_new'),
    url(r'^settings/', views.settings, name='settings'),
    url(r'^parsefeed/', views.parse_feed, name='parse_feed'),

    # for parse manually
    url(r'^parse_manual', views.parse_manual),

    # for find all trendy words manually
    url(r'^nltk_manual', views.nltk_all),

    url(r'^nltk/', views.nltk_list, name="nltk"),
    url(r'^ajax_nltk', views.ajax_nltk, name='ajax_nltk'),
    url(r'^word', views.get_by_word_and_date, name='word_by_date'),
    url(r'^trends', views.nltk_all, name='trends'),
    url(r'^streams', views.streams_list, name='twitter_streams'),
    url(r'^tweets/(?P<task_id>.+)', views.tweets_list, name='tweets_list'),
    url(r'^ajax_streams', views.streams_cycle, name='ajax_streams'),
    url(r'^stopstream', views.stop_stream, name='stop_stream'),
    url(r'^startstream', views.new_tweet_stream, name='startstream'),
]
