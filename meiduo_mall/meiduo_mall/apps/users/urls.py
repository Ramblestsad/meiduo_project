#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2020-12-23 17:15:15
LastEditTime: 2021-01-19 19:06:34
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
    # 验证邮箱
    re_path(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    # 收货地址页面
    re_path(r'^addresses/$', views.AddressView.as_view(), name='address'),
    # 新增收货地址
    re_path(r'^addresses/create/$', views.AddressCreateView.as_view()),
    # 更新和删除地址
    re_path(r'^addresses/(?P<address_id>\d+)/$',
            views.UpdateDestroyAddressView.as_view()),
    # 设置默认地址
    re_path(r'^addresses/(?P<address_id>\d+)/default/$',
            views.DefaultAddressView.as_view()),
    # 修改地址标题
    re_path(r'^addresses/(?P<address_id>\d+)/title/$',
            views.UpdateTitleAddressView.as_view()),
    # 修改密码
    re_path(r'^password/$', views.ChangePwdView.as_view(), name='pass'),
]
