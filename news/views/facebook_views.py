# coding=utf-8
import logging

from django.views import generic

from news.models import FacebookPost

__author__ = 'ilov3'
logger = logging.getLogger(__name__)


class FacebookPostView(generic.ListView):
    template_name = 'facebook/posts/posts.html'
    context_object_name = 'facebook_posts'

    def get_queryset(self):
        return FacebookPost.objects.order_by('-created_time')[:20]


