from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.articles_list, name='articles_list'),
    url(r'^feeds/new', views.new_feed, name='feed_new'),
    url(r'^feeds/', views.feeds_list, name='feeds_list'),
    url(r'^ajax_articles', views.ajax_articles, name='ajax_articles'),
    url(r'^parse', views.parse_manual),
    url(r'^nltk', views.nltk_all),
    url(r'^trends', views.nltk_all, name='trends'),
    # url(r'^for_date', views.nltk_for_date), 
    url(r'^for_range', views.nltk_for_range), 
]
