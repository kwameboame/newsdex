from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.articles_list, name='articles_list'),
    url(r'^feeds/new', views.new_feed, name='feed_new'),
    url(r'^feeds/', views.feeds_list, name='feeds_list'),
    url(r'^ajax_articles', views.ajax_articles, name='ajax_articles'),

    # for parse manually
    url(r'^parse_manual', views.parse_manual),

    # for find all trendy words manually
    url(r'^nltk_manual', views.nltk_all),

    url(r'^nltk/', views.nltk_list, name="nltk"),
    url(r'^ajax_nltk', views.ajax_nltk, name='ajax_nltk'),
    url(r'^word', views.get_by_word_and_date, name='word_by_date'),
    url(r'^trends', views.nltk_all, name='trends'),
]
