#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-01-18 16:09:14
LastEditTime: 2021-01-18 16:25:59
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''


from django.urls import path, re_path

from areas import views


urlpatterns = [
    #省市区三级联动
    re_path(r'^areas/$', views.AreasView.as_view()),
]
