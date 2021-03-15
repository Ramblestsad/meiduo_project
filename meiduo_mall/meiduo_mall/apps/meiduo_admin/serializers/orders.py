#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-15 13:54:55
Description: None
Version: 1.0
License: None
"""

from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods
from goods.models import SKU


class SKUSerializer(serializers.ModelSerializer):

    class Meta:

        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializer(serializers.ModelSerializer):

    sku = SKUSerializer()

    class Meta:

        model = OrderGoods
        fields = ('count', 'sku', 'price')


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""

    skus = OrderGoodsSerializer(many=True)

    class Meta:

        model = OrderInfo
        fields = "__all__"
