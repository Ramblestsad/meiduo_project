#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-01-11 16:07:25
LastEditTime: 2021-01-11 16:28:30
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''


from django.urls import path, re_path

from . import views


urlpatterns = [
    # 提供QQ登录扫码页面
    re_path(r'^qq/login/$', views.QQAuthURLView.as_view()),
    # 处理QQ登录回调
    re_path(r'^oauth_callback/$', views.QQAuthUserView.as_view()),
]
