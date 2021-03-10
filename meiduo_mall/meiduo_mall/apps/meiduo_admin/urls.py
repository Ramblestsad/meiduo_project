#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-10 15:33:39
Description: None
Version: 1.0
License: None
"""


from django.urls import re_path
from rest_framework_jwt.views import obtain_jwt_token

from .views import statistical


urlpatterns = [
    # 登录
    re_path(r'^authorizations/$', obtain_jwt_token),
    # --------数据统计--------
    # 1.用户总量
    re_path(r'^statistical/total_count/$', statistical.UserCountView.as_view()),
]
