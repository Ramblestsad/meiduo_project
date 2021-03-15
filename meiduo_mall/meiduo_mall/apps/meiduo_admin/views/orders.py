#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-15 13:54:36
Description: None
Version: 1.0
License: None
"""

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser

from orders.models import OrderInfo
from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.orders import OrderSerializer


class OrderView(ReadOnlyModelViewSet):
    """查询/修改订单"""

    permission_classes = [IsAdminUser]
    queryset = OrderInfo.objects.all().order_by('id')
    pagination_class = PageNum
    serializer_class = OrderSerializer

    def get_queryset(self):
        """orders获取单一信息"""

        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return OrderInfo.objects.all().order_by('id')
        else:
            return OrderInfo.objects.filter(order_id__contains=keyword).order_by('id')
