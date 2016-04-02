import datetime
from django.db import models

# Create your models here.
from django.db.models import Count, Case, When, F, Func


class WordQueryset(models.QuerySet):
    def ignore_case(self):
        return self.annotate(iword=Func(F('word'), function='LOWER'))

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
        date_from_lookup = "%s__created_time__date__gte" % field
        date_to_lookup = "%s__created_time__date__lte" % field
        count_lookup = "%s_count" % field
        return self \
                   .filter(**{date_from_lookup: date_from, date_to_lookup: date_to}) \
                   .ignore_case() \
                   .values('iword') \
                   .annotate(**{count_lookup: Count(Case(When(**{date_from_lookup: date_from, date_to_lookup: date_to, 'then': F(field)})), distinct=True)}) \
                   .order_by("-%s" % count_lookup)[:count]

    def tracked(self):
        result = []
        tracked = self.filter(tracked=True).ignore_case()
        for word in tracked:
            result.append((word.iword, self.ignore_case()
                           .filter(iword=word.iword)
                           .aggregate(articles_count=Count('article', distinct=True),
                                      posts_count=Count('facebookpost', distinct=True),
                                      comments_count=Count('facebookcomment', distinct=True))))
        return result


class Feed(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Word(models.Model):
    word = models.CharField(max_length=200)
    pos = models.CharField(max_length=20, blank=True, null=True)
    tracked = models.BooleanField(default=False)
    created_time = models.DateTimeField(default=datetime.datetime.now)
    objects = WordQueryset.as_manager()

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['-tracked', 'word']
        unique_together = ("word", "pos")


class Article(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=200)
    url = models.URLField()
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
    post_id = models.CharField(max_length=255)
    words = models.ManyToManyField(Word)

    def __str__(self):
        return "%s..." % self.text[:40]


class FacebookUser(models.Model):
    user_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class FacebookComment(models.Model):
    post_id = models.ForeignKey(FacebookPost, blank=True, null=True)
    user_id = models.ForeignKey(FacebookUser)
    created_time = models.DateTimeField()
    message = models.TextField()
    comment_id = models.CharField(max_length=255)
    words = models.ManyToManyField(Word)

    def __str__(self):
        return "%s..." % self.message[:40]
