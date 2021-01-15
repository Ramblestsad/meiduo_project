#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-01-15 15:10:58
LastEditTime: 2021-01-15 15:13:34
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''


from django.contrib.auth.mixins import LoginRequiredMixin
from django import http

from meiduo_mall.utils.response_code import RETCODE


class LoginRequiredJsonMixin(LoginRequiredMixin):
    """自定义判断用户是否登录的扩展类：返回Json"""

    def handle_no_permission(self):
        """直接响应Json数据"""

        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})
