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
from django.utils.timezone import make_aware, now
import datetime

from users.models import User
from goods.models import GoodsVisitCount
from meiduo_admin.serializers.statistical import GoodsCategoryDailySerializer


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
            'count': count,
            'date': now_date
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
            'count': count,
            'date': now_date
        })


class DayActiveView(APIView):
    """日活用户统计: 当天登录过的用户"""

    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):

        # 获取当天日期
        now_date = datetime.date.today()

        # 获取当天登录过用户总量
        count = User.objects.filter(last_login__gte=now_date).count()

        # 返回结果
        return Response({
            'count': count,
            'date': now_date
        })


class DayOrderView(APIView):
    """日下单用户统计"""

    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):

        # 获取当天日期
        now_date = datetime.date.today()

        # 获取当天下订单用户总量
        count = len(set(User.objects.filter(
            orders__create_time__gte=now_date)))

        # 返回结果
        return Response({
            'count': count,
            'date': now_date
        })


class MonthIncreUserView(APIView):
    """月新增用户:一个月内每天注册的用户"""

    def get(self, request):

        # 获取当前日期
        now_date = datetime.date.today()

        # 获取一个月前日期
        start_date = now_date - datetime.timedelta(days=29)

        # 创建空列表保存每天新增用户量
        date_list = []

        for i in range(30):

            # 日期逐步增加
            index_date = start_date + datetime.timedelta(days=i)
            # 第二天日期
            next_date = start_date + datetime.timedelta(days=i+1)

            # 数据查询
            count = User.objects.filter(
                date_joined__gte=index_date, date_joined__lt=next_date).count()

            # 构造返回数据列表
            date_list.append({
                'count': count,
                'date': index_date
            })

        return Response(date_list)


class GoodsCategoryDailyView(APIView):
    """日分类商品访问量统计"""

    def get(self, request):

        # 获取当天日期
        now_date = datetime.date.today()

        # 获取当天访问的商品分类数量信息
        data = GoodsVisitCount.objects.filter(date__gte=now_date)

        # 序列化返回分类数量
        ser = GoodsCategoryDailySerializer(data, many=True)

        return Response(ser.data)
