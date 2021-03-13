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

from goods.models import SKU, GoodsCategory, SPUSpecification, SpecificationOption


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


class SpecsOptionSerializer(serializers.ModelSerializer):
    """规格选项序列化器"""

    class Meta:

        model = SpecificationOption
        fields = "__all__"


class SPUSpecsSerializer(serializers.ModelSerializer):
    """SPU规格序列化器"""

    options = SpecsOptionSerializer(many=True)
    # specsoption_set = SpecificationOption(many=True) tip: 没有指定副表 relateed_name时

    class Meta:

        model = SPUSpecification
        fields = "__all__"
