from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(FacebookComment)
admin.site.register(FacebookUser)
admin.site.register(FacebookPage)
admin.site.register(FacebookPost)
admin.site.register(Feed)
admin.site.register(Article)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word',)
    search_fields = ['word']  # change this to "search_fields = ['word__icontains']" after going from sqLite


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('iword', 'tracked')
    search_fields = ['iword']  # change this to "search_fields = ['iword__icontains']" after going from sqLite
