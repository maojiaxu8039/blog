#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/9 1:04
# @Author  : maojx
# @Site    : 
# @File    : feels.py
# @Software: PyCharm
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post


class LatestPostsFeed(Feed):
    title = 'My blog'
    link = '/blog/'
    description = "New posts of my blog."

    # title，link，description属性各自对应RSS中的<title>,<link>,<description>
    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.body, 30)
