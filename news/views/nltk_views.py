# coding=utf-8
import datetime
import logging

from django.http import Http404
from django.shortcuts import redirect, render
from django.views import generic

from news.models import Article, FacebookPost, FacebookComment, Word, Tag, FilteredWord
from news.tasks import nltk_all_task

__author__ = 'ilov3'
logger = logging.getLogger(__name__) 


# NLTK
# sudo pip install -U nltk
# python
# >>> import nltk
# >>> nltk.download('stopwords')
# >>> nltk.download('punkt')
# >>> nltk.download('wordnet')
# >>> exit()

def nltk_all(request):
    nltk_all_task.delay()
    return redirect('articles_list')


def nltk_list(request):
    return render(request, 'news/nltk_list.html', {})


def ajax_nltk(request):
    context = {}
    try:
        date_from = datetime.datetime.strptime(request.GET['date_from'], "%Y-%m-%d")
    except:
        date_from = datetime.datetime.today() - datetime.timedelta(days=5)
    try:
        date_to = datetime.datetime.strptime(request.GET['date_to'], "%Y-%m-%d")
    except:
        date_to = datetime.datetime.today()

    date_to = date_to.replace(hour=23, minute=59, second=59)
    context['date_from'] = date_from.strftime("%Y-%m-%d")
    context['date_to'] = date_to.strftime("%Y-%m-%d")

    context['articles_words'] = Tag.objects.get_top('article', date_from, date_to, 15)
    context['posts_words'] = Tag.objects.get_top('facebookpost', date_from, date_to, 15)
    context['comments_words'] = Tag.objects.get_top('facebookcomment', date_from, date_to, 15)

    return render(request, 'news/nltk_cycle.html', context=context)


def get_by_word_and_date(request):
    context = {}
    try:
        word = request.GET['word']
        context['word'] = word
    except:
        raise Http404('No word sent')

    try:
        kinds = {
            'article': {'model': Article, 'verbose_name': 'Articles'},
            'post': {'model': FacebookPost, 'verbose_name': 'Facebook posts'},
            'comment': {'model': FacebookComment, 'verbose_name': 'Facebook comments'}
        }
        tag = Tag.objects.get(iword=word.lower())
        word_set = tag.word_set.all()
        kind = request.GET.get('kind')
        if kind in kinds:
            qs = kinds[kind]['model'].objects.filter(words__in=word_set)
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            if date_from and date_to:
                qs = qs.filter(created_time__date__gte=date_from, created_time__date__lte=date_to)
            context['kind'] = kind
            context['kind_verbose'] = kinds[kind]['verbose_name']
            context['items'] = qs
        else:
            context['articles'] = Article.objects.filter(words__in=word_set)
            context['posts'] = FacebookPost.objects.filter(words__in=word_set)
            context['comments'] = FacebookComment.objects.filter(words__in=word_set)
    except Exception as e:
        logger.error('Error: %s on word: %s.' % (e, word))
    return render(request, 'news/word.html', context=context)


class TrackedWordView(generic.ListView):
    template_name = 'tracked/tracked.html'
    context_object_name = 'tracked_words'

    def get_queryset(self):
        return Tag.objects.tracked()


class FilteredWordView(generic.ListView):
    context_object_name = 'filtered_words'
    petition = FilteredWord
    queryset = FilteredWord.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles_words'] = Tag.objects.tracked_for_articles()
        context['posts_words'] = Tag.objects.tracked_for_posts()
        context['comments_words'] = Tag.objects.tracked_for_comments()
        return context
