#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2020-12-23 17:15:15
LastEditTime: 2020-12-23 17:23:35
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
]
