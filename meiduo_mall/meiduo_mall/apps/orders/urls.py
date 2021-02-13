#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-02-13 15:05:24
LastEditTime: 2021-02-13 15:07:39
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''

from django.urls import re_path

from . import views


urlpatterns = [
    # 订单结算页面
    re_path(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
]