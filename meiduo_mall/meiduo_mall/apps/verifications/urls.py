#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2020-12-29 15:53:09
LastEditTime: 2020-12-31 17:47:16
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2020 Chris W.
'''

from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    re_path(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
]
