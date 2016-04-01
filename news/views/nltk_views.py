# coding=utf-8
import datetime
import logging
import operator

from django.http import Http404
from django.shortcuts import redirect, render
from django.views import generic

from news.models import Article, FacebookPost, FacebookComment, Word
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
    try:
        date_from = datetime.datetime.strptime(request.GET['date_from'], "%Y-%m-%d")
    except:
        date_from = datetime.datetime.today() - datetime.timedelta(days=5)
    try:
        date_to = datetime.datetime.strptime(request.GET['date_to'], "%Y-%m-%d")
    except:
        date_to = datetime.datetime.today()

    date_to = date_to.replace(hour=23, minute=59, second=59)

    articles = Article.objects.filter(publication_date__range=[date_from, date_to])
    articles_words = {}
    print(date_from)
    print(date_to)
    for article in articles:
        for word in article.words.all():
            try:
                articles_words[word.word] = articles_words[word.word] + 1
            except:
                articles_words[word.word] = 1

    posts_words = {}
    posts = FacebookPost.objects.filter(created_time__range=[date_from, date_to])
    for post in posts:
        for word in post.words.all():
            try:
                posts_words[word.word] = posts_words[word.word] + 1
            except:
                posts_words[word.word] = 1

    comments_words = {}
    comments = FacebookComment.objects.filter(created_time__range=[date_from, date_to])
    for comment in comments:
        for word in comment.words.all():
            try:
                comments_words[word.word] = comments_words[word.word] + 1
            except:
                comments_words[word.word] = 1

    articles_words = sorted(articles_words.items(), key=operator.itemgetter(1), reverse=True)[:15]
    posts_words = sorted(posts_words.items(), key=operator.itemgetter(1), reverse=True)[:15]
    comments_words = sorted(comments_words.items(), key=operator.itemgetter(1), reverse=True)[:15]

    return render(request, 'news/nltk_cycle.html', locals())  # {'rows' : rows})


def get_by_word_and_date(request):
    try:
        word = request.GET['word']
    except:
        raise Http404('No word sent')

    try:
        word = Word.objects.filter(word=word).last()
        articles = Article.objects.filter(words__word__iregex='^%s$' % word.word)
        posts = FacebookPost.objects.filter(words__word__iregex='^%s$' % word.word)
        comments = FacebookComment.objects.filter(words__word__iregex='^%s$' % word.word)
    except Exception as e:
        logger.error('Error: %s on word: %s.' % (e, word))
    return render(request, 'news/word.html', locals())


class TrackedWordView(generic.ListView):
    template_name = 'tracked/tracked.html'
    context_object_name = 'tracked_words'

    def get_queryset(self):
        return Word.objects.filter(tracked=True).order_by('-created_time')[:20]
