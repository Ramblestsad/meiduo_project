#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-12 15:12:41
Description: None
Version: 1.0
License: None
"""


from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from meiduo_admin.utils import PageNum
from goods.models import SKUImage
from meiduo_admin.serializers.images import ImagesSerializer


class ImagesView(ModelViewSet):
    """图片表管理"""

    permission_classes = [IsAdminUser]

    queryset = SKUImage.objects.all().order_by('sku_id')
    serializer_class = ImagesSerializer
    pagination_class = PageNum
