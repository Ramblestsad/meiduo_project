#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-12 15:19:26
Description: None
Version: 1.0
License: None
"""


from rest_framework import serializers

from goods.models import SKUImage, SKU


class ImagesSerializer(serializers.ModelSerializer):
    """SKU图片表序列化器"""

    sku_id = serializers.IntegerField()

    class Meta:

        model = SKUImage
        fields = "__all__"


class SKUSerializer(serializers.ModelSerializer):
    """SKU商品信息序列化器"""

    class Meta:

        model = SKU
        fields = ('id', 'name')
