#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/9 12:08
# @Author  : maojx
# @Site    : 
# @File    : search_indexes.py
# @Software: PyCharm
from haystack import indexes
from .models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    publish = indexes.DateTimeField(model_attr='publish')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().published.all()
