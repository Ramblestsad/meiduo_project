#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-16 19:45:25
Description: None
Version: 1.0
License: None
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission

from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.groups import GroupsSerializer
from meiduo_admin.serializers.permission import PermissionsSerializer


class GroupsView(ModelViewSet):
    """分组group的管理"""

    permission_classes = [IsAdminUser]
    pagination_class = PageNum
    queryset = Group.objects.all().order_by('id')
    serializer_class = GroupsSerializer

    def simple(self, reqeust):
        """获取权限表数据"""

        pers = Permission.objects.all().order_by('id')
        ser = PermissionsSerializer(pers, many=True) # 使用以前定义的全选序列化器

        return Response(ser.data)
