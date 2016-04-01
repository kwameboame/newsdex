# coding=utf-8
import logging

import nltk
import requests
from nltk.corpus import wordnet

__author__ = 'ilov3'
logger = logging.getLogger(__name__)
FACEBOOK_CLIENT_ID = '105323143198945'
FACEBOOK_CLIENT_SECRET = 'e10beb3dc3a388480927d29493168545'


def get_access_token(client_id, client_secret):
    url = 'https://graph.facebook.com/oauth/access_token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',

    }
    req = requests.get(url, params=params)
    s = req.text.split('=')
    if (s[0] == 'access_token') and (len(s) == 2):
        return s[1]
    else:
        return None


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
