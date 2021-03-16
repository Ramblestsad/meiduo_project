#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-16 20:16:49
Description: None
Version: 1.0
License: None
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import Group

from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.administrator import AdministratorSerializer
from meiduo_admin.serializers.groups import GroupsSerializer
from users.models import User


class AdministratorView(ModelViewSet):
    """分组group的管理"""

    permission_classes = [IsAdminUser]
    pagination_class = PageNum
    queryset = User.objects.filter(is_staff=True).order_by('id')
    serializer_class = AdministratorSerializer

    # 获取分组数据

    def simple(self, reqeust):

        pers = Group.objects.all()
        ser = GroupsSerializer(pers, many=True)

        return Response(ser.data)
