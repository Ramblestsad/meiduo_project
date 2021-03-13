#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-13 17:20:27
Description: None
Version: 1.0
License: None
"""


from rest_framework import serializers

from goods.models import SKU, GoodsCategory


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""

    class Meta:

        model = SKU
        fields = "__all__"


class SKUCategorySerailizer(serializers.ModelSerializer):
    """商品分类序列化器"""
    class Meta:

        model = GoodsCategory
        fields = '__all__'
