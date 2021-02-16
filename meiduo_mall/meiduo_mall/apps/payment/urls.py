#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-02-16 13:17:18
LastEditTime: 2021-02-16 14:12:39
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''

from django.urls import path, re_path

from . import views


urlpatterns = [
    # 支付：支付宝
    re_path(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),
    # 保存订单支付结果
    re_path(r'^payment/status/$', views.PaymentStatusView.as_view()),
]
