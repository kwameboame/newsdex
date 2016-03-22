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


""" NLTK """
    articles
# sudo pip install -U nltk
# python
# >>> import nltk
# >>> nltk.download('stopwords')
# >>> nltk.download('punkt')
# >>> nltk.download('wordnet')
# >>> exit()


import nltk
from nltk.corpus import wordnet
 
 
def wordnet_pos_code(tag):
    if tag in ['NN', 'NNS', 'NNP', 'NNPS',]:
        return wordnet.NOUN
    elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', ]:
        return wordnet.VERB
    elif tag in ['JJ', 'JJR', 'JJS',]:
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
    tagged_words = [(tagged_word[0].lower(), tagged_word[1]) for tagged_word in tagged_words]
 
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
            words.append(lemmatizer.lemmatize(tagged_word[0], pos=pos))
 
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
    articles = Article.objects.all()
    
    for article in articles:
        print('Get article:')
        print(article.title)
        words = get_most_common_words(article.content, 10, remove_stopwords=True)
        print('Words are:')
        for word in words:
            print(word['word'])
            try:
                new_word = Word.objects.get(word=word['word'])
            except:
                new_word = Word(word=word['word'])
                new_word.save()
                print('Thats new word!')
            try:
                if not article.words.filter(word=new_word).exists():
                    article.words.add(new_word)
                    article.save()
                    print('Word added to article')
            except:
                print('something went wrong')
            
            
@print_http_response
def nltk_all(request):