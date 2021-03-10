#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-10 19:24:38
Description: None
Version: 1.0
License: None
"""


from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
import datetime

from users.models import User


class UserCountView(APIView):
    """用户总量统计"""

    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):

        # 获取当天日期
        now_date = datetime.date.today()

        # 获取用户总量
        count = User.objects.all().count()

        # 返回结果
        return Response({
            'date': now_date,
            'count': count
        })


class DayIncreView(APIView):
    """日新增用户统计"""

    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):

        # 获取当天日期
        now_date = datetime.date.today()

        # 获取当天新注册用户总量
        count = User.objects.filter(date_joined__gte=now_date).count()

        # 返回结果
        return Response({
            'date': now_date,
            'count': count
        })
