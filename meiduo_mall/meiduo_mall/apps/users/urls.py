#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2020-12-23 17:15:15
LastEditTime: 2021-01-15 14:41:55
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2020 Chris W.
'''


from django.urls import path, re_path
from . import views

urlpatterns = [
    # 用户注册
    re_path(r'^register$', views.RegisterView.as_view(), name='register'),
    # 判断用户名是否重复注册
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count',
            views.UsernameCountView.as_view(), name='ucount'),
    # 判断手机号是否重复注册
    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count', views.MobileCountView.as_view(),
            name='mcount'),
    # 用户登录
    re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    # 用户退出登录
    re_path(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # 用户中心
    re_path(r'^info/$', views.UserInfoView.as_view(), name='info'),
    # 添加邮箱
    re_path(r'^emails/$', views.EmailView.as_view()),
]
