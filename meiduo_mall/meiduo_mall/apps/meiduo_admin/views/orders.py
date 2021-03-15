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
from rest_framework.response import Response
from rest_framework.decorators import action

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

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        """修改订单状态"""

        # 查询要修改的订单对象
        try:
            order = OrderInfo.objects.get(order_id=pk)
        except:
            return Response({'error': '订单编号错误'})

        # 修改订单状态
        # - 获取订单状态
        status = request.data.get('status')
        if status is None:
            return Response({'error': '缺少状态值'})
        order.status = status
        order.save

        # 返回结果
        return Response({
            'order_id': pk,
            'stauts': status
        })
