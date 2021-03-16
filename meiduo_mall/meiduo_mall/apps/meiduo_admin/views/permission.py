#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-16 18:36:35
Description: None
Version: 1.0
License: None
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.permission import PermissionsSerializer, ContentTypeSerializer


class PermissionsView(ModelViewSet):
    """权限管理"""

    permission_classes = [IsAdminUser]
    serializer_class = PermissionsSerializer
    queryset = Permission.objects.all().order_by('id')
    pagination_class = PageNum

    def content_type(self, request):
        """获取权限类型"""

        # 查询全部分类
        conetent = ContentType.objects.all().order_by('id')

        # 返回结果
        ser = ContentTypeSerializer(conetent, many=True)

        return Response(ser.data)
