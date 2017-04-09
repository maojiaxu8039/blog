#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/9 0:34
# @Author  : maojx
# @Site    : 
# @File    : sitemaps.py
# @Software: PyCharm

from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    # changefreq和priority属性表明了帖子页面修改的频率和它们在网站中的关联性（最大值是1）

    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.publish
