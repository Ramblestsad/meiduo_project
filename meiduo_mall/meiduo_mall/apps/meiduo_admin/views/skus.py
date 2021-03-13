#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-13 17:18:07
Description: None
Version: 1.0
License: None
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.skus import SKUSerializer
from goods.models import SKU


class SKUView(ModelViewSet):
    """SKUS管理"""

    permission_classes = [IsAdminUser]

    queryset = SKU.objects.all().order_by('id')
    serializer_class = SKUSerializer
    pagination_class = PageNum
