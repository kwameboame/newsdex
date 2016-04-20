import datetime
from django.db import models

# Create your models here.
from django.db.models import Count, Case, When, F


class TagQuerySet(models.QuerySet):
    def tracked(self):
        return self.filter(tracked=True).annotate(
                articles_count=Count('word__article', distinct=True),
                posts_count=Count('word__facebookpost', distinct=True),
                comments_count=Count('word__facebookcomment', distinct=True),
        )

    def get_top(self, field, date_from, date_to, count):
        """
        Returns top trending words (ignore case search) for given range of dates
        :param count: offset
        :type count: int
        :param date_to:
        :type date_to:
        :param date_from:
        :type date_from:
        :param field: one of the following: article | facebookpost | facebookcomment
        :type field: str
        """
        date_from_lookup = "word__%s__created_time__date__gte" % field
        date_to_lookup = "word__%s__created_time__date__lte" % field
        count_lookup = "%s_count" % field
        return self \
                   .filter(**{date_from_lookup: date_from, date_to_lookup: date_to}) \
                   .annotate(**{count_lookup: Count(Case(When(**{date_from_lookup: date_from, date_to_lookup: date_to, 'then': F('word__%s' % field)})), distinct=True)}) \
                   .order_by("-%s" % count_lookup)[:count]


class Feed(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Tag(models.Model):
    iword = models.CharField(max_length=200, unique=True)
    tracked = models.BooleanField(default=False)
    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.iword

    class Meta:
        ordering = ['-tracked', 'iword']


class Word(models.Model):
    word = models.CharField(max_length=200)
    pos = models.CharField(max_length=20, blank=True, null=True)
    created_time = models.DateTimeField(default=datetime.datetime.now)
    tag = models.ForeignKey(Tag)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['word']
        unique_together = ("word", "pos")


class Article(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=200, unique=True)
    url = models.URLField(unique=True)
    description = models.TextField()
    content = models.TextField(default="")
    created_time = models.DateTimeField()
    words = models.ManyToManyField(Word)

    def __str__(self):
        return self.title


class FacebookPage(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class FacebookPost(models.Model):
    parent_page = models.ForeignKey(FacebookPage)
    created_time = models.DateTimeField()
    text = models.TextField()
    post_id = models.CharField(max_length=255, unique=True)
    words = models.ManyToManyField(Word)

    def __str__(self):
        return "%s..." % self.text[:40]


class FacebookUser(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class FacebookComment(models.Model):
    post_id = models.ForeignKey(FacebookPost, blank=True, null=True)
    user_id = models.ForeignKey(FacebookUser)
    created_time = models.DateTimeField()
    message = models.TextField()
    comment_id = models.CharField(max_length=255, unique=True)
    words = models.ManyToManyField(Word)

    def __str__(self):
        return "%s..." % self.message[:40]

class WordsFilter(models.Model):
    filtered_word = models.CharField(default="", null=False, max_length=255)

    def __str__(self):
        return self.word