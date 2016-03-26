from django.db import models

# Create your models here.

class Feed(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Tracked_Word(models.Model):
    tracked_word = models.CharField(max_length=100)

    def __str__(self):
        return self.tracked_word
        

class Word(models.Model):
    word = models.CharField(max_length=200)
    
    def __str__(self):
        return self.word


class Article(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField()
    content = models.TextField(default="")
    publication_date = models.DateTimeField()
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

    def __str__(self):
        return self.post_id
        
        
class FacebookUser(models.Model):
    user_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.user_id        
        
        
class FacebookComment(models.Model):
    post_id = models.ForeignKey(FacebookPost, blank=True, null=True)
    user_id = models.ForeignKey(FacebookUser)
    created_time = models.DateTimeField()
    message = models.TextField()
    comment_id = models.CharField(max_length=255)

    def __str__(self):
        return self.comment_id