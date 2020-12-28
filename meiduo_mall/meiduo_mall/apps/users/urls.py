#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2020-12-23 17:15:15
LastEditTime: 2020-12-28 21:45:05
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2020 Chris W.
'''


from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^register$', views.RegisterView.as_view(), name='register'),
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count', views.UsernameCountView.as_view(), name='ucount'),
    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count', views.MobileCountView.as_view(), name='mcount'),
]
