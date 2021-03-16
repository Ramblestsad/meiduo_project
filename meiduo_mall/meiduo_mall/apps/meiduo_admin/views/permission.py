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
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Permission

from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.permission import PermissionsSerializer


class PermissionsView(ModelViewSet):
    """权限管理"""

    permission_classes = [IsAdminUser]
    serializer_class = PermissionsSerializer
    queryset = Permission.objects.all().order_by('id')
    pagination_class = PageNum
