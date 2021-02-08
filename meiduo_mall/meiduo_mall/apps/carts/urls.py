#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-02-08 14:47:15
LastEditTime: 2021-02-08 14:48:41
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''


from django.urls import re_path

from . import views


urlpatterns = [
    # 购物车管理
    re_path(r'^carts/$', views.CartsView.as_view(), name='info'),
]