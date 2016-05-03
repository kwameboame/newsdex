# coding=utf-8
import logging

import nltk
from nltk.corpus import wordnet

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


def get_nltk_stop_words():
    return set(nltk.corpus.stopwords.words('english'))


def get_most_common_words(text, words_count, remove_stopwords=False):
    # NLTK's default stopwords
    stopwords = get_nltk_stop_words()

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
