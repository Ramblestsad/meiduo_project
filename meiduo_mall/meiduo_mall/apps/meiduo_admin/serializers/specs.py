#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-12 13:37:20
Description: None
Version: 1.0
License: None
"""


from rest_framework import serializers

from goods.models import SPUSpecification, SPU


class SpecsSerializer(serializers.ModelSerializer):
    """商品规格的序列化器"""

    # 指定关联外键数据返回形式
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    class Meta:

        model = SPUSpecification
        fields = "__all__"


class SPUSerializer(serializers.ModelSerializer):
    """
        SPU商品信息序列化器
    """

    class Meta:

        model = SPU
        fields = ('id', 'name')
