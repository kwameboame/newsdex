import sys
import operator

from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import nltk
from nltk.corpus import wordnet

from .models import *
from .forms import FeedForm
from .tasks import parse_all_task


# NLTK
# sudo pip install -U nltk
# python
# >>> import nltk
# >>> nltk.download('stopwords')
# >>> nltk.download('punkt')
# >>> nltk.download('wordnet')
# >>> exit()


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
        return HttpResponse(['<BR>' if c == '\n' else c for c in printed.content])

    return new_f


def articles_list(request):
    articles = Article.objects.all().order_by('-publication_date')
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
        rows = [articles[x:x + 1] for x in range(0, len(articles), 1)]

    return render(request, 'news/articles_cycle.html', locals())  # {'rows' : rows})


class FacebookPostView(generic.ListView):
    template_name = 'facebook/posts/posts.html'
    context_object_name = 'facebook_posts'

    def get_queryset(self):
        return FacebookPost.objects.order_by('-created_time')[:20]


###Feeds Listing
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
                parse_all_task.delay(feed_url=url)
            return redirect('news.views.feeds_list')
    else:
        form = FeedForm()
    return render(request, 'news/new_feed.html', {'form': form})


@print_http_response
def parse_manual(request):
    parse_all_task.delay()


def wordnet_pos_code(tag):
    if tag in ['NN', 'NNS', 'NNP', 'NNPS', ]:
        return wordnet.NOUN
    elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', ]:
        return wordnet.VERB
    elif tag in ['JJ', 'JJR', 'JJS', ]:
        return wordnet.ADJ
    elif tag in ['RB', 'RBR', 'RBS', ]:
        return wordnet.ADV
    else:
        return None


# Retuns % words_count % most common words in % text %
# Output format: [ {'word': 'word1, 'count': 'count1}, {'word': 'word2, 'count': 'count2}, ... etc]
# Where count - frequency of occurrence of the word in the text
def get_most_common_words(text, words_count, remove_stopwords=False):
    # NLTK's default stopwords
    stopwords = set(nltk.corpus.stopwords.words('english'))

    # Making a list of tagged words
    tagged_words = nltk.word_tokenize(text)
    tagged_words = nltk.pos_tag(tagged_words)

    # Make all words lower case
    # tagged_words = [(tagged_word[0].lower(), tagged_word[1]) for tagged_word in tagged_words]

    # Remove single-character tokens (mostly punctuation)
    tagged_words = [tagged_word for tagged_word in tagged_words if len(tagged_word[0]) > 1]

    # Remove numbers
    tagged_words = [tagged_word for tagged_word in tagged_words if not tagged_word[0].isnumeric()]

    # Remove stopwords
    if remove_stopwords:
        tagged_words = [tagged_word for tagged_word in tagged_words if tagged_word[0] not in stopwords]

    # Dark magic
    lemmatizer = nltk.stem.WordNetLemmatizer()
    words = []
    for tagged_word in tagged_words:
        pos = wordnet_pos_code(tagged_word[1])
        # Ignoring all words, except nouns, verbs, adjectives and adverbs
        if pos is not None:
            words.append((lemmatizer.lemmatize(tagged_word[0], pos=pos), tagged_word[1]))

    # Calculate frequency distribution
    fdist = nltk.FreqDist(words)

    # Return top % words_count % words
    res = []
    for word, frequency in fdist.most_common(words_count):
        word_dict = {}
        word_dict['word'] = word
        word_dict['count'] = frequency
        res.append(word_dict)
    return res


"""
# Example
text = 'The best way to troubleshoot this is to actually look in Wordnet. Take a look here: Loving in wordnet. As you ' \
      'can see, there is actually an adjective "loving" present in Wordnet. As a matter of fact, there is even the ' \
      'adverb "lovingly": lovingly in Wordnet. Because wordnet doesnt actually know what part of speech you actually ' \
      'want, it defaults to noun (n in Wordnet). If you are using Penn Treebank tag set, heres some handy function for ' \
      'transforming Penn to WN tags: walk walking walked walker make made made make making maker'
 
words = get_most_common_words(text, 10, remove_stopwords=True)
for word in words:
   print(word['word'] + ' ' + str(word['count']))
"""


@print_http_response
def nltk_all(request):
    def add_words(queryset, lookup_title, lookup_content):
        for obj in queryset:
            print('Get %s:' % obj._meta.model_name)
            print(getattr(obj, lookup_title))
            words = get_most_common_words(getattr(obj, lookup_content), 10, remove_stopwords=True)
            print('Words are:')
            for word in words:
                word, pos = word['word']
                print(word)
                try:
                    new_word = Word.objects.get(Q(word__iregex='^%s$' % word), Q(pos=pos) | Q(tracked=True))  # => word='^word$' AND (pos=pos OR tracked=True)
                    if new_word.tracked and not obj.words.filter(word=new_word).exists():
                        obj.words.add(new_word)
                        obj.save()
                        print('Tracked word "%s" added to %s' % (word, obj._meta.model_name))
                    print('Word exists in db')
                except Word.DoesNotExist:  # lets specify our exception
                    new_word = Word(word=word, pos=pos)
                    new_word.save()
                    print('Thats new word!')
                except Word.MultipleObjectsReturned:
                    print('Word "%s" has duplicates!' % word)
                try:
                    if not obj.words.filter(word=new_word).exists():
                        obj.words.add(new_word)
                        obj.save()
                        print('Word added to %s' % obj._meta.model_name)
                    else:
                        print('Word exists in %s' % obj._meta.model_name)
                except Exception as e:  # and even if we don't know what it actually was catch it and print or log it
                    print('Something went wrong! The error was: %s' % e)

    articles = Article.objects.all()
    posts = FacebookPost.objects.all()
    comments = FacebookComment.objects.all()

    add_words(articles, 'title', 'content')
    add_words(posts, 'post_id', 'text')
    add_words(comments, 'comment_id', 'message')


class TrackedWordView(generic.ListView):
    template_name = 'tracked/tracked.html'
    context_object_name = 'tracked_words'

    def get_queryset(self):
        return Word.objects.filter(tracked=True).order_by('-created_time')[:20]


@print_http_response
def nltk_for_date(request):
    try:
        date = datetime.datetime.strptime(request.GET['date'], "%Y-%m-%d").date()
    except:
        date = datetime.date.today()
    articles = Article.objects.filter(publication_date__contains=date)
    trend_words = {}
    print(date)
    for article in articles:
        for word in article.words.all():
            try:
                trend_words[word.word] = trend_words[word.word] + 1
            except:
                trend_words[word.word] = 1

    posts = FacebookPost.objects.filter(created_time__contains=date)
    trend_words2 = {}
    for post in posts:
        for word in post.words.all():
            try:
                trend_words2[word.word] = trend_words2[word.word] + 1
            except:
                trend_words2[word.word] = 1

    comments = FacebookComment.objects.filter(created_time__contains=date)
    trend_words3 = {}
    for comment in comments:
        for word in comment.words.all():
            try:
                trend_words3[word.word] = trend_words3[word.word] + 1
            except:
                trend_words3[word.word] = 1

    sorted_words = sorted(trend_words.items(), key=operator.itemgetter(1), reverse=True)
    sorted_words2 = sorted(trend_words2.items(), key=operator.itemgetter(1), reverse=True)
    sorted_words3 = sorted(trend_words3.items(), key=operator.itemgetter(1), reverse=True)

    print('Articles top words')
    for key, value in sorted_words:
        print(key)
        print(value)

    print('FacebookPost top words')
    for key, value in sorted_words2:
        print(key)
        print(value)

    print('FacebookComment top words')
    for key, value in sorted_words3:
        print(key)
        print(value)


@print_http_response
def nltk_for_range(request):
    try:
        date_from = datetime.datetime.strptime(request.GET['date_from'], "%Y-%m-%d")
    except:
        date_from = datetime.date.today() - datetime.timedelta(days=5)
    try:
        date_to = datetime.datetime.strptime(request.GET['date_to'], "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except:
        date_to = datetime.date.today().replace(hour=23, minute=59, second=59)

    articles = Article.objects.filter(publication_date__range=[date_from, date_to])
    trend_words = {}
    print(date_from)
    print(date_to)
    for article in articles:
        for word in article.words.all():
            try:
                trend_words[word.word] = trend_words[word.word] + 1
            except:
                trend_words[word.word] = 1

    trend_words2 = {}
    posts = FacebookPost.objects.filter(created_time__range=[date_from, date_to])
    for post in posts:
        for word in post.words.all():
            try:
                trend_words2[word.word] = trend_words2[word.word] + 1
            except:
                trend_words2[word.word] = 1

    trend_words3 = {}
    comments = FacebookComment.objects.filter(created_time__range=[date_from, date_to])
    for comment in comments:
        for word in comment.words.all():
            try:
                trend_words3[word.word] = trend_words3[word.word] + 1
            except:
                trend_words3[word.word] = 1

    sorted_words = sorted(trend_words.items(), key=operator.itemgetter(1), reverse=True)
    sorted_words2 = sorted(trend_words2.items(), key=operator.itemgetter(1), reverse=True)
    sorted_words3 = sorted(trend_words3.items(), key=operator.itemgetter(1), reverse=True)

    print('Articles top words')
    for key, value in sorted_words:
        print(key)
        print(value)

    print('FacebookPost top words')
    for key, value in sorted_words2:
        print(key)
        print(value)

    print('FacebookComment top words')
    for key, value in sorted_words3:
        print(key)
        print(value)
