#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/8 11:41
# @Author  : maojx
# @Site    : 
# @File    : from.py.py
# @Software: PyCharm

from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    # required=False让comments的字段可选 widget 改变空间的属性可以重写默认控件 input改成Textarea
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        # 使用fields 列表你可以明确的告诉框架你想在你的表单中包含哪些字段，或者使用exclude 列表定义你想排除在外的那些字段
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    query = forms.CharField()
