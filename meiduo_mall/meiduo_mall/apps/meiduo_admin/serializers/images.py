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

from goods.models import SKUImage


class ImagesSerializer(serializers.ModelSerializer):
    """SKU图片表序列化器"""

    sku_id = serializers.IntegerField()

    class Meta:

        model = SKUImage
        fields = "__all__"
