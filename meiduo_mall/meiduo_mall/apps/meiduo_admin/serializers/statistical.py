#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-10 21:19:20
Description: None
Version: 1.0
License: None
"""


from rest_framework import serializers

from goods.models import GoodsVisitCount


class GoodsCategoryDailySerializer(serializers.ModelSerializer):
    """日分类物品访问量的序列化器"""

    # 嵌套序列化返回字段指定值
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ('category', 'count')
