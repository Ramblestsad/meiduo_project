#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-11 18:27:58
Description: None
Version: 1.0
License: None
"""


from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser

from users.models import User
from meiduo_admin.serializers.users import UsersSerializer
from meiduo_admin.utils import PageNum


class UsersView(ListCreateAPIView):
    """获取用户数据"""

    permission_classes = [IsAdminUser]

    # 指定查询集，重写 get_queryset 方法后就不会调用下面的queryset了
    # queryset = User.objects.all().order_by('id')

    # 指定序列化器: 多个业务调用一个serializer可能会漏掉某些字段
    serializer_class = UsersSerializer

    # 使用分页器
    pagination_class = PageNum

    # 重写获取query_set的方法
    def get_queryset(self):

        if self.request.query_params.get('keyword') == '':
            return User.objects.all().order_by('id')
        else:
            username = self.request.query_params.get('keyword')
            # username__contains 模糊查询
            return User.objects.filter(username__contains=username).order_by('id')
